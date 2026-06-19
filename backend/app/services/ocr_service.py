"""PaddleOCR AIStudio 异步 OCR 调用

官方 API 文档：https://aistudio.baidu.com/paddleocr
流程：
  1. POST /api/v2/ocr/jobs  (multipart: file + model) -> jobId
  2. GET  /api/v2/ocr/jobs/{jobId}  轮询 -> 拿到 OCR 结果
"""
from __future__ import annotations

import asyncio
import time
from typing import Any

import httpx

from app.core.config import settings


async def _submit_job(client: httpx.AsyncClient, image_bytes: bytes, filename: str) -> str:
    """提交 OCR 任务，返回 jobId"""
    files = {"file": (filename, image_bytes, "image/jpeg")}
    data = {"model": settings.PADDLE_OCR_MODEL}
    headers = {"Authorization": f"token {settings.PADDLE_OCR_TOKEN}"}
    resp = await client.post(
        settings.PADDLE_OCR_URL,
        files=files,
        data=data,
        headers=headers,
        timeout=settings.PADDLE_OCR_TIMEOUT,
    )
    resp.raise_for_status()
    payload = resp.json()

    # 兼容多种返回结构
    if "data" in payload and isinstance(payload["data"], dict):
        job_id = payload["data"].get("jobId") or payload["data"].get("job_id")
    else:
        job_id = payload.get("jobId") or payload.get("job_id")

    if not job_id:
        raise RuntimeError(f"OCR 任务提交成功但未返回 jobId：{payload}")
    return str(job_id)


async def _poll_result(client: httpx.AsyncClient, job_id: str) -> dict[str, Any]:
    """轮询直到 OCR 完成或超时"""
    headers = {"Authorization": f"token {settings.PADDLE_OCR_TOKEN}"}
    url = f"{settings.PADDLE_OCR_URL.rstrip('/')}/{job_id}"

    for _ in range(settings.PADDLE_OCR_MAX_POLLS):
        resp = await client.get(url, headers=headers, timeout=settings.PADDLE_OCR_TIMEOUT)
        resp.raise_for_status()
        payload = resp.json()

        # 兼容嵌套 data
        data = payload.get("data", payload)
        status = (data.get("status") or "").lower()

        if status in {"done", "success", "finished", "completed"}:
            return data
        if status in {"failed", "error", "failure"}:
            raise RuntimeError(f"OCR 任务失败：{payload}")

        await asyncio.sleep(settings.PADDLE_OCR_POLL_INTERVAL)

    raise TimeoutError(f"OCR 任务 {job_id} 轮询超时")


def _extract_texts(payload: dict[str, Any]) -> list[dict[str, Any]]:
    """把 OCR 返回结构统一成 [{text, score, box}, ...]"""
    # 常见返回：{"data": {"result": {"ocrResults": [...]}}}
    result = payload.get("result") or payload.get("data", {}).get("result", {})
    ocr_results = (
        result.get("ocrResults")
        or result.get("results")
        or result.get("pages")
        or payload.get("ocrResults")
        or []
    )
    items: list[dict[str, Any]] = []
    # 多页情况
    pages = ocr_results if isinstance(ocr_results, list) and ocr_results and isinstance(ocr_results[0], dict) and "prunedResult" in ocr_results[0] else None
    if pages:
        for page in ocr_results:
            pruned = page.get("prunedResult") or page.get("rec_texts") or []
            if isinstance(pruned, dict):
                texts = pruned.get("rec_texts", [])
                scores = pruned.get("rec_scores", [])
                boxes = pruned.get("rec_boxes", [])
                for i, t in enumerate(texts):
                    items.append({
                        "text": t,
                        "score": scores[i] if i < len(scores) else None,
                        "box": boxes[i] if i < len(boxes) else None,
                    })
            elif isinstance(pruned, list):
                # rec_texts 形式
                if pruned and isinstance(pruned[0], str):
                    scores = page.get("rec_scores") or []
                    boxes = page.get("rec_boxes") or []
                    for i, t in enumerate(pruned):
                        items.append({
                            "text": t,
                            "score": scores[i] if i < len(scores) else None,
                            "box": boxes[i] if i < len(boxes) else None,
                        })
                else:
                    # 旧格式：[ [box, (text, score)], ... ]
                    for line in pruned:
                        if isinstance(line, (list, tuple)) and len(line) >= 2:
                            text_score = line[1]
                            if isinstance(text_score, (list, tuple)) and len(text_score) >= 2:
                                items.append({"text": text_score[0], "score": text_score[1], "box": line[0]})
                            else:
                                items.append({"text": str(text_score), "score": None, "box": line[0]})
    elif isinstance(ocr_results, list) and ocr_results and isinstance(ocr_results[0], dict) and "text" in ocr_results[0]:
        items = ocr_results
    return items


async def recognize_image(image_bytes: bytes, filename: str = "book.jpg") -> dict[str, Any]:
    """主入口：传入图片二进制，返回统一结构 {texts, raw}"""
    start = time.time()
    async with httpx.AsyncClient() as client:
        job_id = await _submit_job(client, image_bytes, filename)
        payload = await _poll_result(client, job_id)
    texts = _extract_texts(payload)
    return {
        "job_id": job_id,
        "texts": texts,
        "raw": payload,
        "elapsed": round(time.time() - start, 2),
    }

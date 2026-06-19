"""图片识别编排：OCR → 大模型结构化 → 大模型导师纠错"""
from __future__ import annotations

import logging
from typing import Any

from app.services.llm_service import correct_listing, structure_books
from app.services.ocr_service import recognize_image

logger = logging.getLogger(__name__)


def _fallback_from_ocr(ocr_texts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """当 LLM 不可用时，兜底把每段 OCR 文本当成一本书"""
    out = []
    for i, t in enumerate(ocr_texts):
        text = (t.get("text") or "").strip()
        if not text or len(text) < 2:
            continue
        out.append({
            "title": text,
            "author": None,
            "publisher": None,
            "isbn": None,
            "edition": None,
            "raw_ocr": text,
            "confidence": t.get("score"),
            "position": i,
        })
    return out


async def recognize_books(image_bytes: bytes, filename: str = "book.jpg") -> dict[str, Any]:
    """主流程：上传一摞书照片 → 返回结构化书单 + 原始 OCR"""
    ocr_result = await recognize_image(image_bytes, filename)
    ocr_texts = ocr_result.get("texts", [])
    raw_lines = [t.get("text", "") for t in ocr_texts if t.get("text")]

    # 第一步：LLM 结构化
    structured = await structure_books(raw_lines)

    books: list[dict[str, Any]] = []
    if structured:
        # 把 OCR 信心值带回
        for i, b in enumerate(structured):
            b.setdefault("position", i)
            b.setdefault("raw_ocr", raw_lines[i] if i < len(raw_lines) else None)
            books.append(b)
    else:
        books = _fallback_from_ocr(ocr_texts)

    # 第二步：导师纠错
    if books and any(b.get("title") for b in books):
        books = await correct_listing(books)

    return {
        "raw_text": "\n".join(raw_lines),
        "texts": ocr_texts,
        "books": books,
        "ocr_job_id": ocr_result.get("job_id"),
        "elapsed": ocr_result.get("elapsed"),
    }

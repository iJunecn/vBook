"""大模型调用服务（agnes-2.0-flash，OpenAI 兼容接口）

注意：agnes-ai.com 官方文档使用的 base URL 在不同区域可能不同。
为灵活起见，base URL 和 model 都通过 .env 配置，默认使用 OpenAI 兼容格式。
如需切换为其它兼容服务（OpenAI、DeepSeek、Anthropic、SiliconFlow 等），
只需修改 .env 中的 AGNES_BASE_URL 和 AGNES_MODEL。
"""
from __future__ import annotations

import json
import logging
from typing import Any

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


def _chat_url() -> str:
    base = settings.AGNES_BASE_URL.rstrip("/")
    # 兼容：用户写完整 chat/completions 或仅 base
    if base.endswith("/chat/completions"):
        return base
    if base.endswith("/v1") or base.endswith("/v1/"):
        return f"{base.rstrip('/')}/chat/completions"
    return f"{base}/v1/chat/completions"


def _build_prompt(ocr_texts: list[str]) -> str:
    """构造识别 prompt：要求 LLM 把 OCR 文本片段整理成结构化书单"""
    numbered = "\n".join(f"{i + 1}. {t}" for i, t in enumerate(ocr_texts))
    return f"""你是一个中文图书信息整理助手。下面是从一摞书的书脊侧面 OCR 出来的原始文字片段（顺序是从左到右 / 从上到下）。
请根据这些文字片段，识别出每本书的：书名(title)、作者(author)、出版社(publisher)、版次(edition)、ISBN。
要求：
1. 只输出严格的 JSON 数组，不要输出其它任何文字或 markdown 标记。
2. 数组每个元素包含字段：title, author, publisher, edition, isbn。如果某字段无法判断，置为 null。
3. 合并同一本书的多个碎片（例如 title 在一段、author 在另一段）。
4. 忽略明显噪声（页码、"目录"、单字符、标点）。
5. 书名要尽量完整。author 写成"张三"形式，不要加"著/编"等后缀。
6. 如果 OCR 文本不像是书，title 字段保留原文即可。

OCR 片段：
{numbered}

请直接输出 JSON 数组："""


def _parse_json(content: str) -> list[dict[str, Any]]:
    """从模型回复中尽量鲁棒地提取 JSON 数组"""
    content = content.strip()
    # 去掉 markdown 代码块
    if content.startswith("```"):
        # 去掉首尾 ```
        lines = content.splitlines()
        # 去掉首行 ```json / ``` 和最后一行 ```
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        content = "\n".join(lines).strip()

    # 直接 parse
    try:
        data = json.loads(content)
        if isinstance(data, list):
            return data
        if isinstance(data, dict) and "books" in data:
            return data["books"]
    except json.JSONDecodeError:
        pass

    # 截取第一个 [ 到最后一个 ]
    start = content.find("[")
    end = content.rfind("]")
    if start != -1 and end != -1 and end > start:
        try:
            data = json.loads(content[start : end + 1])
            if isinstance(data, list):
                return data
        except json.JSONDecodeError:
            pass
    return []


async def structure_books(ocr_texts: list[str]) -> list[dict[str, Any]]:
    """调用大模型把 OCR 文本整理成结构化书单"""
    if not ocr_texts:
        return []
    if not settings.AGNES_API_KEY:
        logger.warning("AGNES_API_KEY 未配置，跳过大模型结构化步骤")
        return []

    prompt = _build_prompt(ocr_texts)
    url = _chat_url()
    payload = {
        "model": settings.AGNES_MODEL,
        "messages": [
            {"role": "system", "content": "你是中文图书信息整理助手，只输出严格 JSON。"},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
        "max_tokens": 2048,
    }
    headers = {
        "Authorization": f"Bearer {settings.AGNES_API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=settings.AGNES_TIMEOUT) as client:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
    except Exception as e:
        logger.exception("调用 agnes API 失败：%s", e)
        return []

    try:
        content = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        logger.error("agnes 返回结构异常：%s", data)
        return []

    return _parse_json(content)


async def correct_listing(books: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """导师纠错：让 LLM 再检查一遍识别结果中的书名错误

    例如：把"高数"纠正为"高等数学"，把"机概"纠正为"机械原理"等。
    """
    if not books or not settings.AGNES_API_KEY:
        return books

    prompt = (
        "你是一个中文教材纠错助手。下面是从一摞书的书脊 OCR + 大模型识别出的书单，"
        "可能存在缩写（如'高数'='高等数学'、'大物'='大学物理'）、错字、出版社和作者缺失等问题。"
        "请根据你对中国高校常见教材的理解，纠正书名（如果是明显缩写或错字），补充作者和出版社（如你能确认）。\n"
        "只输出严格 JSON 数组，每个元素字段：title, author, publisher, edition, isbn。"
        "如果原信息已是正确且完整，则原样保留。\n\n"
        + json.dumps(books, ensure_ascii=False, indent=2)
    )
    url = _chat_url()
    payload = {
        "model": settings.AGNES_MODEL,
        "messages": [
            {"role": "system", "content": "你是中文图书校对助手，只输出严格 JSON。"},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.1,
        "max_tokens": 2048,
    }
    headers = {
        "Authorization": f"Bearer {settings.AGNES_API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=settings.AGNES_TIMEOUT) as client:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
        content = data["choices"][0]["message"]["content"]
        corrected = _parse_json(content)
        if corrected and len(corrected) == len(books):
            return corrected
    except Exception as e:
        logger.exception("导师纠错步骤失败：%s", e)

    return books

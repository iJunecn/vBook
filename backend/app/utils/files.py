"""文件保存工具"""
import os
import uuid
from pathlib import Path

from fastapi import UploadFile

from app.core.config import settings


async def save_upload(file: UploadFile) -> str:
    """保存上传的图片到本地，返回 URL 路径"""
    suffix = Path(file.filename or "").suffix.lower() or ".jpg"
    if suffix not in {".jpg", ".jpeg", ".png", ".webp"}:
        suffix = ".jpg"
    name = f"{uuid.uuid4().hex}{suffix}"
    dest = Path(settings.UPLOAD_DIR) / name
    content = await file.read()
    if len(content) > settings.MAX_UPLOAD_SIZE:
        raise ValueError(f"文件大小超过限制 {settings.MAX_UPLOAD_SIZE // 1024 // 1024}MB")
    dest.write_bytes(content)
    # 返回相对 URL，前端通过 /uploads/<filename> 访问
    return f"/uploads/{name}"

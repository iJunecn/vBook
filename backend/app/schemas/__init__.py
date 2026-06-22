"""Pydantic 模型 - 请求/响应数据契约"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ---- User ----
class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=32, pattern=r"^[A-Za-z0-9_\-]+$")
    email: EmailStr
    password: str = Field(min_length=6, max_length=64)
    nickname: Optional[str] = None
    campus: Optional[str] = None


class UserLogin(BaseModel):
    """账号密码登录：`account` 可以是用户名或邮箱（后端自动识别）"""

    account: str = Field(min_length=3, max_length=120, description="用户名或邮箱")
    password: str = Field(min_length=6, max_length=64)


class WeChatLoginIn(BaseModel):
    """微信小程序登录：前端 uni.login 拿到的临时 code"""

    code: str = Field(min_length=1, max_length=128)


class UserUpdate(BaseModel):
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    campus: Optional[str] = None


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: EmailStr
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    campus: Optional[str] = None
    created_at: datetime


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ---- Book ----
class BookBase(BaseModel):
    title: str
    author: Optional[str] = None
    publisher: Optional[str] = None
    isbn: Optional[str] = None
    edition: Optional[str] = None
    price: float = 5.0


class BookCreate(BookBase):
    pass


class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    publisher: Optional[str] = None
    isbn: Optional[str] = None
    edition: Optional[str] = None
    price: Optional[float] = None
    status: Optional[str] = None


class BookOut(BookBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    listing_id: int
    status: str
    confidence: Optional[float] = None
    position: int
    created_at: datetime


# ---- Listing ----
class ListingCreate(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    description: Optional[str] = None
    campus: Optional[str] = None
    default_price: float = 5.0
    books: list[BookCreate]


class ListingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    seller_id: int
    title: str
    description: Optional[str] = None
    cover_image: str
    campus: Optional[str] = None
    default_price: float
    status: str
    created_at: datetime
    updated_at: datetime
    books: list[BookOut]
    seller: Optional[UserOut] = None


class ListingSummary(BaseModel):
    """首页/列表用的精简信息"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    cover_image: str
    campus: Optional[str] = None
    default_price: float
    status: str
    created_at: datetime
    book_count: int
    available_count: int
    seller: Optional[UserOut] = None


# ---- OCR 识别 ----
class RecognizeResultBook(BaseModel):
    title: str
    author: Optional[str] = None
    publisher: Optional[str] = None
    isbn: Optional[str] = None
    edition: Optional[str] = None
    price: float = 5.0
    confidence: Optional[float] = None
    raw_ocr: Optional[str] = None
    position: int = 0


class RecognizeResult(BaseModel):
    image_url: str
    books: list[RecognizeResultBook]
    raw_text: str
    model: str


# ---- Order ----
class OrderCreate(BaseModel):
    book_id: int
    note: Optional[str] = None


class OrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    book_id: int
    buyer_id: int
    seller_id: int
    price: float
    status: str
    note: Optional[str] = None
    created_at: datetime
    book: Optional[BookOut] = None


# ---- 通用 ----
class Message(BaseModel):
    detail: str

"""图书与上架接口"""
import io
import json
import logging
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_current_user, get_current_user_optional
from app.core.config import settings
from app.db.session import get_db
from app.models import Book, BookListing, User
from app.schemas import (
    BookOut,
    BookUpdate,
    ListingOut,
    ListingSummary,
    RecognizeResult,
    RecognizeResultBook,
    UserOut,
)
from app.services.recognition_service import recognize_books
from app.utils.files import save_upload

router = APIRouter(tags=["books"])
logger = logging.getLogger(__name__)


# ---- 识别（不落库）----
@router.post("/recognize", response_model=RecognizeResult)
async def api_recognize(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
):
    """上传一摞书侧面照片，返回识别出的书单（不落库）"""
    if file.content_type not in settings.allowed_image_type_list:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "仅支持 JPG/PNG/WEBP 图片")
    image_bytes = await file.read()
    # 先把图片保存到磁盘，再调识别服务
    file.file = io.BytesIO(image_bytes)  # type: ignore[assignment]
    image_url = await save_upload(file)
    try:
        result = await recognize_books(image_bytes, file.filename or "book.jpg")
    except Exception as e:
        logger.exception("识别失败：%s", e)
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, f"识别服务异常：{e}")
    books = [RecognizeResultBook(**b) for b in result["books"]]
    return RecognizeResult(
        image_url=image_url,
        books=books,
        raw_text=result["raw_text"],
        model=settings.AGNES_MODEL,
    )


# ---- 上架（封面 + 书单 JSON 一次提交）----
@router.post("/listings/with-image", response_model=ListingOut)
async def create_listing_with_image(
    title: str = Form(...),
    description: Optional[str] = Form(None),
    campus: Optional[str] = Form(None),
    default_price: float = Form(5.0),
    cover: UploadFile = File(...),
    books_json: str = Form(..., description="JSON 字符串：书单数组"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """上传封面 + 书单 JSON，一次性上架"""
    if cover.content_type not in settings.allowed_image_type_list:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "封面必须是 JPG/PNG/WEBP")
    image_url = await save_upload(cover)
    try:
        books_data = json.loads(books_json)
        if not isinstance(books_data, list) or not books_data:
            raise ValueError("books_json 必须是非空数组")
    except Exception as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"books_json 解析失败：{e}")

    listing = BookListing(
        seller_id=user.id,
        title=title.strip()[:120],
        description=description,
        cover_image=image_url,
        campus=campus or user.campus,
        default_price=default_price,
    )
    db.add(listing)
    db.flush()

    for i, b in enumerate(books_data):
        if not b.get("title"):
            continue
        book = Book(
            listing_id=listing.id,
            title=str(b["title"]).strip()[:255],
            author=(b.get("author") or None),
            publisher=(b.get("publisher") or None),
            isbn=(b.get("isbn") or None),
            edition=(b.get("edition") or None),
            price=float(b.get("price") or default_price),
            raw_ocr=b.get("raw_ocr"),
            confidence=b.get("confidence"),
            position=i,
        )
        db.add(book)

    db.commit()
    db.refresh(listing)
    return _serialize_listing(listing)


# ---- 列表 / 详情 ----
@router.get("/listings", response_model=list[ListingSummary])
def list_listings(
    db: Session = Depends(get_db),
    q: Optional[str] = Query(default=None, description="按书名/作者/出版社模糊搜索"),
    campus: Optional[str] = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=50),
):
    stmt = (
        select(BookListing)
        .options(selectinload(BookListing.books), selectinload(BookListing.seller))
        .where(BookListing.status == "active")
        .order_by(BookListing.created_at.desc())
    )
    if campus:
        stmt = stmt.where(BookListing.campus == campus)
    if q:
        like = f"%{q}%"
        stmt = stmt.where(
            or_(
                BookListing.title.ilike(like),
                BookListing.id.in_(
                    select(Book.listing_id).where(
                        or_(
                            Book.title.ilike(like),
                            Book.author.ilike(like),
                            Book.publisher.ilike(like),
                        )
                    )
                ),
            )
        )
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)
    rows = db.execute(stmt).scalars().unique().all()
    return [
        ListingSummary(
            id=r.id,
            title=r.title,
            cover_image=r.cover_image,
            campus=r.campus,
            default_price=r.default_price,
            status=r.status,
            created_at=r.created_at,
            book_count=len(r.books),
            available_count=sum(1 for b in r.books if b.status == "available"),
            seller=UserOut.model_validate(r.seller) if r.seller else None,
        )
        for r in rows
    ]


@router.get("/listings/{listing_id}", response_model=ListingOut)
def get_listing(
    listing_id: int,
    db: Session = Depends(get_db),
):
    stmt = (
        select(BookListing)
        .options(selectinload(BookListing.books), selectinload(BookListing.seller))
        .where(BookListing.id == listing_id)
    )
    listing = db.execute(stmt).scalar_one_or_none()
    if not listing:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "上架记录不存在")
    return _serialize_listing(listing)


@router.delete("/listings/{listing_id}")
def delete_listing(
    listing_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    listing = db.get(BookListing, listing_id)
    if not listing:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "上架记录不存在")
    if listing.seller_id != user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "只能下架自己的书")
    listing.status = "removed"
    db.commit()
    return {"detail": "已下架"}


# ---- 单本书编辑 ----
@router.patch("/books/{book_id}", response_model=BookOut)
def update_book(
    book_id: int,
    payload: BookUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    book = db.get(Book, book_id)
    if not book:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "书不存在")
    if book.listing.seller_id != user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "只能修改自己上架的书")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(book, k, v)
    db.commit()
    db.refresh(book)
    return BookOut.model_validate(book)


@router.delete("/books/{book_id}")
def delete_book(
    book_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    book = db.get(Book, book_id)
    if not book:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "书不存在")
    if book.listing.seller_id != user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "无权删除")
    db.delete(book)
    db.commit()
    return {"detail": "已删除"}


# ---- 用户主页 ----
@router.get("/users/{user_id}/listings", response_model=list[ListingSummary])
def user_listings(
    user_id: int,
    db: Session = Depends(get_db),
):
    stmt = (
        select(BookListing)
        .options(selectinload(BookListing.books), selectinload(BookListing.seller))
        .where(BookListing.seller_id == user_id)
        .order_by(BookListing.created_at.desc())
    )
    rows = db.execute(stmt).scalars().unique().all()
    return [
        ListingSummary(
            id=r.id,
            title=r.title,
            cover_image=r.cover_image,
            campus=r.campus,
            default_price=r.default_price,
            status=r.status,
            created_at=r.created_at,
            book_count=len(r.books),
            available_count=sum(1 for b in r.books if b.status == "available"),
            seller=UserOut.model_validate(r.seller) if r.seller else None,
        )
        for r in rows
    ]


def _serialize_listing(listing: BookListing) -> ListingOut:
    books_sorted = sorted(listing.books, key=lambda b: b.position)
    return ListingOut(
        id=listing.id,
        seller_id=listing.seller_id,
        title=listing.title,
        description=listing.description,
        cover_image=listing.cover_image,
        campus=listing.campus,
        default_price=listing.default_price,
        status=listing.status,
        created_at=listing.created_at,
        updated_at=listing.updated_at,
        books=[BookOut.model_validate(b) for b in books_sorted],
        seller=UserOut.model_validate(listing.seller) if listing.seller else None,
    )

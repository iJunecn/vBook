"""订单接口"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models import Book, BookListing, Order, User
from app.schemas import BookOut, OrderCreate, OrderOut

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("", response_model=OrderOut)
def create_order(
    payload: OrderCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    book = db.get(Book, payload.book_id)
    if not book:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "书不存在")
    if book.status != "available":
        raise HTTPException(status.HTTP_409_CONFLICT, "该书已售出")
    listing = db.get(BookListing, book.listing_id)
    if not listing:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "上架记录不存在")
    if listing.seller_id == user.id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "不能购买自己上架的书")

    order = Order(
        book_id=book.id,
        buyer_id=user.id,
        seller_id=listing.seller_id,
        price=book.price,
        note=payload.note,
        status="paid",
    )
    book.status = "sold"
    db.add(order)
    db.commit()
    db.refresh(order)
    return _serialize_order(order, book)


@router.get("/mine", response_model=list[OrderOut])
def my_orders(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    stmt = (
        select(Order)
        .where(or_(Order.buyer_id == user.id, Order.seller_id == user.id))
        .order_by(Order.created_at.desc())
    )
    rows = db.execute(stmt).scalars().all()
    out: list[OrderOut] = []
    for o in rows:
        book = db.get(Book, o.book_id)
        out.append(_serialize_order(o, book))
    return out


@router.get("/sales", response_model=list[OrderOut])
def my_sales(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    stmt = (
        select(Order)
        .where(Order.seller_id == user.id)
        .order_by(Order.created_at.desc())
    )
    rows = db.execute(stmt).scalars().all()
    out: list[OrderOut] = []
    for o in rows:
        book = db.get(Book, o.book_id)
        out.append(_serialize_order(o, book))
    return out


def _serialize_order(o: Order, book: Book | None) -> OrderOut:
    return OrderOut(
        id=o.id,
        book_id=o.book_id,
        buyer_id=o.buyer_id,
        seller_id=o.seller_id,
        price=o.price,
        status=o.status,
        note=o.note,
        created_at=o.created_at,
        book=BookOut.model_validate(book) if book else None,
    )

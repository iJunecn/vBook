"""认证相关接口"""
import secrets

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.security import create_access_token, hash_password, verify_password
from app.db.session import get_db
from app.models import User
from app.schemas import TokenOut, UserCreate, UserLogin, UserOut, UserUpdate, WeChatLoginIn

router = APIRouter(prefix="/auth", tags=["auth"])

WECHAT_CODE2SESSION_URL = "https://api.weixin.qq.com/sns/jscode2session"


@router.post("/register", response_model=TokenOut)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    exists = (
        db.query(User)
        .filter(or_(User.username == payload.username, User.email == payload.email))
        .first()
    )
    if exists:
        raise HTTPException(status.HTTP_409_CONFLICT, "用户名或邮箱已被使用")
    user = User(
        username=payload.username,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        nickname=payload.nickname or payload.username,
        campus=payload.campus,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token(user.id, {"username": user.username})
    return TokenOut(access_token=token, user=UserOut.model_validate(user))


@router.post("/login", response_model=TokenOut)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    """账号密码登录：`account` 字段支持用户名或邮箱，自动判别。"""
    account = payload.account.strip()
    # 用 or_ 一次性查用户名或邮箱；用 lower 让邮箱大小写不敏感
    user = (
        db.query(User)
        .filter(
            or_(
                User.username == account,
                func.lower(User.email) == account.lower(),
            )
        )
        .first()
    )
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "用户名/邮箱或密码错误")
    if not user.is_active:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "账号已停用")
    token = create_access_token(user.id, {"username": user.username})
    return TokenOut(access_token=token, user=UserOut.model_validate(user))


@router.post("/wechat-login", response_model=TokenOut)
async def wechat_login(payload: WeChatLoginIn, db: Session = Depends(get_db)):
    """微信小程序一键登录：code -> openid -> 签发 JWT（按需自动注册）"""
    if not settings.WECHAT_APPID or not settings.WECHAT_SECRET:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "服务端未配置微信登录")
    params = {
        "appid": settings.WECHAT_APPID,
        "secret": settings.WECHAT_SECRET,
        "js_code": payload.code,
        "grant_type": "authorization_code",
    }
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(WECHAT_CODE2SESSION_URL, params=params)
            data = resp.json()
    except Exception as e:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, f"微信登录服务异常：{e}")

    openid = data.get("openid")
    if not openid:
        # 微信返回 errcode/errmsg（如 code 无效、AppID 不匹配等）
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            f"微信登录失败：{data.get('errmsg') or data.get('errcode') or '未知错误'}",
        )

    user = db.query(User).filter(User.openid == openid).first()
    if not user:
        # 首次登录：用 openid 派生占位用户名/邮箱以满足非空约束，昵称头像可后续修改
        suffix = openid[:12]
        user = User(
            openid=openid,
            username=f"wx_{suffix}",
            email=f"{suffix}@wx.local",
            hashed_password=hash_password(secrets.token_urlsafe(16)),
            nickname="微信用户",
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    elif not user.is_active:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "账号已停用")

    token = create_access_token(user.id, {"username": user.username})
    return TokenOut(access_token=token, user=UserOut.model_validate(user))


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return UserOut.model_validate(user)


@router.patch("/me", response_model=UserOut)
def update_me(payload: UserUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(user, k, v)
    db.commit()
    db.refresh(user)
    return UserOut.model_validate(user)

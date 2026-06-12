import httpx
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..config import WECHAT_APPID, WECHAT_SECRET
from ..database import get_db
from ..models import User
from ..schemas import LoginRequest, APIResponse
from ..auth import create_token

router = APIRouter(prefix="/api/auth", tags=["认证"])

WECHAT_LOGIN_URL = "https://api.weixin.qq.com/sns/jscode2session"


@router.post("/dev-login")
async def dev_login(db: Session = Depends(get_db)):
    openid = "dev_user_001"
    user = db.query(User).filter(User.openid == openid).first()
    is_new = False
    if not user:
        user = User(openid=openid, nickname="开发测试用户")
        db.add(user)
        db.commit()
        db.refresh(user)
        is_new = True

    token = create_token(user.id, openid)
    return APIResponse(data={
        "token": token,
        "user_info": {
            "openid": user.openid,
            "nickname": user.nickname,
            "avatar_url": user.avatar_url
        },
        "is_new_user": is_new
    }).model_dump()


@router.post("/login")
async def login(req: LoginRequest, db: Session = Depends(get_db)):
    if not WECHAT_APPID:
        return APIResponse(code=4001, message="微信 AppID 未配置，开发阶段请使用 POST /api/auth/dev-login").model_dump()

    async with httpx.AsyncClient() as client:
        resp = await client.get(WECHAT_LOGIN_URL, params={
            "appid": WECHAT_APPID,
            "secret": WECHAT_SECRET,
            "js_code": req.code,
            "grant_type": "authorization_code"
        })
        wx_data = resp.json()

    if "errcode" in wx_data and wx_data["errcode"] != 0:
        return APIResponse(code=4001, message=f"微信登录失败: {wx_data.get('errmsg', '')}").model_dump()

    openid = wx_data["openid"]

    user = db.query(User).filter(User.openid == openid).first()
    is_new = False
    if not user:
        user = User(openid=openid, nickname="微信用户")
        db.add(user)
        db.commit()
        db.refresh(user)
        is_new = True

    token = create_token(user.id, openid)

    return APIResponse(data={
        "token": token,
        "user_info": {
            "openid": user.openid,
            "nickname": user.nickname,
            "avatar_url": user.avatar_url
        },
        "is_new_user": is_new
    }).model_dump()

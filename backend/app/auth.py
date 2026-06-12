from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi import Header, HTTPException
from .config import JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRE_DAYS


def create_token(user_id: int, openid: str) -> str:
    payload = {
        "user_id": user_id,
        "openid": openid,
        "exp": datetime.utcnow() + timedelta(days=JWT_EXPIRE_DAYS)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="token 无效或已过期")


def get_current_user(authorization: str = Header(default="")) -> dict:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未提供 token")
    token = authorization[7:]
    return decode_token(token)

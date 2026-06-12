from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User
from ..schemas import UpdateProfileRequest, APIResponse, UserProfile
from ..auth import get_current_user

router = APIRouter(prefix="/api/user", tags=["用户"])


@router.get("/profile")
async def get_profile(
    user_payload: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_payload["user_id"]).first()
    if not user:
        return {"code": 4004, "message": "用户不存在"}

    from ..models import Analysis
    count = db.query(Analysis).filter(Analysis.user_id == user.id).count()

    return APIResponse(data={
        "nickname": user.nickname,
        "avatar_url": user.avatar_url,
        "phone": user.phone,
        "hospital": user.hospital,
        "department": user.department,
        "created_at": user.created_at.isoformat() if user.created_at else "",
        "analysis_count": count
    }).model_dump()


@router.put("/profile")
async def update_profile(
    req: UpdateProfileRequest,
    user_payload: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_payload["user_id"]).first()
    if not user:
        return {"code": 4004, "message": "用户不存在"}

    update_data = req.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)
    db.commit()

    return APIResponse(message="更新成功").model_dump()

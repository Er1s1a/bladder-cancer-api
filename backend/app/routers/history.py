from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Analysis
from ..schemas import HistoryListResponse, APIResponse
from ..auth import get_current_user

router = APIRouter(prefix="/api/history", tags=["分析记录"])


@router.get("")
async def list_history(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=100),
    user_payload: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_id = user_payload["user_id"]
    total = db.query(Analysis).filter(Analysis.user_id == user_id).count()
    records = (
        db.query(Analysis)
        .filter(Analysis.user_id == user_id)
        .order_by(Analysis.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    items = [{
        "analysisId": r.analysis_id,
        "patientId": r.patient_id,
        "analysisTime": r.created_at.strftime("%Y-%m-%d %H:%M") if r.created_at else "",
        "recurrenceRisk": r.recurrence_risk,
        "diseaseProbability": r.disease_probability,
        "riskLevel": r.risk_level,
        "modelVersion": r.model_version
    } for r in records]

    return APIResponse(data={"records": items, "total": total, "page": page, "page_size": page_size}).model_dump()


@router.get("/{analysis_id}")
async def get_detail(
    analysis_id: str,
    user_payload: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    record = (
        db.query(Analysis)
        .filter(Analysis.analysis_id == analysis_id, Analysis.user_id == user_payload["user_id"])
        .first()
    )
    if not record:
        return {"code": 4004, "message": "记录不存在"}

    return APIResponse(data={
        "analysisId": record.analysis_id,
        "patientId": record.patient_id,
        "analysisTime": record.created_at.strftime("%Y-%m-%d %H:%M:%S") if record.created_at else "",
        "modelVersion": record.model_version,
        "recurrenceRisk": record.recurrence_risk,
        "diseaseProbability": record.disease_probability,
        "riskLevel": record.risk_level,
        "clinicalData": record.clinical_data,
        "heatmapData": record.heatmap_data,
        "heatmapInterpretation": record.interpretation,
        "recommendations": record.recommendations
    }).model_dump()

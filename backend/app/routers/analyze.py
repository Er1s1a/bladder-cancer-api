import uuid
from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, Analysis
from ..schemas import AnalyzeRequest, APIResponse
from ..auth import get_current_user
from ..services.model import predict_risk

router = APIRouter(prefix="/api/analyze", tags=["AI分析"])


@router.post("")
async def analyze(
    req: AnalyzeRequest,
    user_payload: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_id = user_payload["user_id"]
    user = db.query(User).filter(User.id == user_id).first()

    # 生成编号
    date_str = datetime.now().strftime("%Y%m%d")
    count = db.query(Analysis).filter(Analysis.user_id == user_id).count()
    analysis_id = f"A{date_str}{count + 1:03d}"
    patient_id = f"PAT-{date_str}"

    # 调用 AI 模型（EORTC 风险量表）
    result = predict_risk(
        dicom_link=req.dicom_link,
        lesion_size=req.lesion_size,
        lesion_count=req.lesion_count,
        tumor_grade=req.tumor_grade,
        invasion_depth=req.invasion_depth,
        lymph_node_metastasis=req.lymph_node_metastasis,
        prior_recurrence=req.prior_recurrence,
        concomitant_cis=req.concomitant_cis
    )

    # 保存记录
    record = Analysis(
        analysis_id=analysis_id,
        user_id=user_id,
        patient_id=patient_id,
        dicom_link=req.dicom_link,
        lesion_size=req.lesion_size,
        lesion_count=req.lesion_count,
        tumor_grade=req.tumor_grade,
        invasion_depth=req.invasion_depth,
        lymph_metastasis=req.lymph_node_metastasis,
        prior_recurrence=req.prior_recurrence,
        concomitant_cis=1 if req.concomitant_cis else 0,
        recurrence_risk=result["recurrence_risk"],
        disease_probability=result["disease_probability"],
        risk_level=result["risk_level"],
        clinical_data=result["clinical_data"],
        heatmap_data=result["heatmap_data"],
        interpretation=result["heatmap_interpretation"],
        recommendations=result["recommendations"],
        model_version=result["model_version"]
    )
    db.add(record)
    db.commit()

    return APIResponse(data={
        "analysisId": analysis_id,
        "patientId": patient_id,
        "analysisTime": record.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        "modelVersion": result["model_version"],
        "recurrenceRisk": result["recurrence_risk"],
        "diseaseProbability": result["disease_probability"],
        "riskLevel": result["risk_level"],
        "clinicalData": result["clinical_data"],
        "heatmapData": result["heatmap_data"],
        "heatmapInterpretation": result["heatmap_interpretation"],
        "recommendations": result["recommendations"]
    }).model_dump()

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# ---------- Auth ----------
class LoginRequest(BaseModel):
    code: str


class LoginResponse(BaseModel):
    token: str
    user_info: dict
    is_new_user: bool


# ---------- Analyze ----------
class AnalyzeRequest(BaseModel):
    model_config = {"populate_by_name": True}

    dicom_link: str = Field(default="", validation_alias="dicomLink", description="DICOM 文件夹链接")
    lesion_size: float = Field(default=0, validation_alias="lesionSize", description="病灶大小 mm")
    lesion_count: int = Field(default=0, validation_alias="lesionCount", description="病灶数量")
    tumor_grade: str = Field(default="", validation_alias="tumorGrade", description="肿瘤分级 G1/G2/G3")
    invasion_depth: str = Field(default="", validation_alias="invasionDepth", description="浸润深度 Ta/T1/T2/T3/T4")
    lymph_node_metastasis: str = Field(default="", validation_alias="lymphNodeMetastasis", description="淋巴结 N0/N1/N2/N3")
    prior_recurrence: str = Field(default="primary", validation_alias="priorRecurrence", description="既往复发情况 primary/≤1 per year/＞1 per year")
    concomitant_cis: bool = Field(default=False, validation_alias="concomitantCis", description="是否合并原位癌 CIS")


class Hotspot(BaseModel):
    x: float
    y: float
    radius: float
    color: str
    intensity: float
    label: str = ""


class AnalyzeResponse(BaseModel):
    analysis_id: str
    patient_id: str
    analysis_time: str
    model_version: str
    recurrence_risk: float
    disease_probability: float
    risk_level: str
    clinical_data: dict
    heatmap_data: dict
    heatmap_interpretation: str
    recommendations: list


# ---------- History ----------
class HistoryItem(BaseModel):
    analysis_id: str
    patient_id: str
    analysis_time: str
    recurrence_risk: float
    risk_level: str
    model_version: str = "v2.1"


class HistoryListResponse(BaseModel):
    records: list
    total: int
    page: int
    page_size: int


# ---------- User ----------
class UserProfile(BaseModel):
    nickname: str
    avatar_url: str
    phone: str
    hospital: str
    department: str
    created_at: datetime
    analysis_count: int


class UpdateProfileRequest(BaseModel):
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    phone: Optional[str] = None
    hospital: Optional[str] = None
    department: Optional[str] = None


# ---------- API Wrapper ----------
class APIResponse(BaseModel):
    code: int = 0
    data: Optional[dict] = None
    message: str = "ok"

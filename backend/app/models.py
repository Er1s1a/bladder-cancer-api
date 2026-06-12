from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    openid = Column(String(64), unique=True, nullable=False, index=True)
    nickname = Column(String(64), default="")
    avatar_url = Column(String(512), default="")
    phone = Column(String(20), default="")
    hospital = Column(String(128), default="")
    department = Column(String(64), default="")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    analyses = relationship("Analysis", back_populates="user")


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    analysis_id = Column(String(32), unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    patient_id = Column(String(32), nullable=False)
    dicom_link = Column(Text, default="")
    lesion_size = Column(Float, default=0)
    lesion_count = Column(Integer, default=0)
    tumor_grade = Column(String(8), default="")
    invasion_depth = Column(String(8), default="")
    lymph_metastasis = Column(String(8), default="")
    prior_recurrence = Column(String(16), default="primary")
    concomitant_cis = Column(Integer, default=0)
    recurrence_risk = Column(Float, default=0)
    disease_probability = Column(Float, default=0)
    risk_level = Column(String(8), default="")
    clinical_data = Column(JSON, default=dict)
    heatmap_data = Column(JSON, default=dict)
    interpretation = Column(Text, default="")
    recommendations = Column(JSON, default=list)
    model_version = Column(String(16), default="v2.1")
    status = Column(String(16), default="completed")
    created_at = Column(DateTime, default=datetime.now)

    user = relationship("User", back_populates="analyses")

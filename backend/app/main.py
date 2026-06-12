from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routers import auth, analyze, history, user

# 自动建表
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="膀胱癌复发评估 API",
    description="膀胱癌复发风险评估系统后端服务",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 路由
app.include_router(auth.router)
app.include_router(analyze.router)
app.include_router(history.router)
app.include_router(user.router)


@app.get("/")
def root():
    return {"message": "膀胱癌复发评估 API 运行中", "version": "1.0.0"}


@app.get("/health")
def health():
    return {"status": "ok"}

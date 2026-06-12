from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from .database import engine, Base
from .routers import auth, analyze, history, user
import os

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="膀胱癌复发评估",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(analyze.router)
app.include_router(history.router)
app.include_router(user.router)

_static_dir = os.path.join(os.path.dirname(__file__), "static")
_assets_dir = os.path.join(_static_dir, "assets")
if os.path.isdir(_assets_dir):
    app.mount("/assets", StaticFiles(directory=_assets_dir), name="assets")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/{path:path}")
async def serve_spa(path: str):
    if path.startswith("api/"):
        return {"message": "Not Found", "code": 404}
    index_path = os.path.join(_static_dir, "index.html")
    if os.path.isfile(index_path):
        return FileResponse(index_path)
    return {"message": "膀胱癌复发评估 运行中"}

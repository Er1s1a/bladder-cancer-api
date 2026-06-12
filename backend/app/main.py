from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from .database import engine, Base
from .routers import auth, analyze, history, user
import os, pathlib

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

_this_file = pathlib.Path(__file__).resolve()
_static_dir = str(_this_file.parent.parent / "static")
_assets_dir = str(_this_file.parent.parent / "static" / "assets")
_public_dir = str(_this_file.parent.parent / "static" / "static")
if os.path.isdir(_assets_dir):
    app.mount("/assets", StaticFiles(directory=_assets_dir), name="assets")
if os.path.isdir(_public_dir):
    app.mount("/static", StaticFiles(directory=_public_dir), name="public")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/")
@app.get("/{path:path}")
async def serve_spa(path: str = ""):
    if path.startswith("api/"):
        return {"message": "Not Found", "code": 404}
    index_path = os.path.join(_static_dir, "index.html")
    if os.path.isfile(index_path):
        return FileResponse(index_path)
    return {"message": "膀胱癌复发评估 运行中"}

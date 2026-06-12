import os

WECHAT_APPID = os.getenv("WECHAT_APPID", "")
WECHAT_SECRET = os.getenv("WECHAT_SECRET", "")

_TURSO_URL = os.getenv("TURSO_URL", "")
_TURSO_TOKEN = os.getenv("TURSO_AUTH_TOKEN", "")

DEFAULT_DB = "sqlite:///./bladder_cancer.db"

if _TURSO_URL and _TURSO_TOKEN:
    _host = _TURSO_URL.replace("libsql://", "")
    DATABASE_URL = f"sqlite+libsql://{_host}?authToken={_TURSO_TOKEN}"
else:
    DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DB)

JWT_SECRET = os.getenv("JWT_SECRET", "change_me")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_DAYS = int(os.getenv("JWT_EXPIRE_DAYS", "30"))

PORT = int(os.getenv("PORT", "8000"))

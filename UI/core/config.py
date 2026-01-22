# UI/core/config.py
import os
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]  # .../NLP-TraCuuPhapDienVN

@dataclass(frozen=True)
class Settings:
    CSV_PATH: str
    CHROMA_DIR: str
    CHROMA_COLLECTION: str
    SQLITE_PATH: str
    EMBED_MODEL_ID: str
    EMBED_DEVICE: str
    DEFAULT_TOP_K: int

def _env(key: str, default: str) -> str:
    v = os.getenv(key)
    return v.strip() if v else default

def _resolve(p: str) -> str:
    raw = Path(p).expanduser()
    if raw.is_absolute():
        return str(raw)

    # ưu tiên resolve theo REPO_ROOT
    cand = (REPO_ROOT / raw).resolve()
    if cand.exists() or cand.parent.exists():
        return str(cand)

    # fallback theo cwd (đỡ đau khi run chỗ khác)
    return str((Path.cwd() / raw).resolve())

def get_settings() -> Settings:
    return Settings(
        CSV_PATH=_resolve(_env("CSV_PATH", "data/pdchude.csv")),
        CHROMA_DIR=_resolve(_env("CHROMA_DIR", "UI/vector_db")),
        CHROMA_COLLECTION=_env("CHROMA_COLLECTION", "iuh_law_advisor_2026"),
        SQLITE_PATH=_resolve(_env("SQLITE_PATH", "UI/data/ui.sqlite3")),
        EMBED_MODEL_ID=_env("EMBED_MODEL_ID", "keepitreal/vietnamese-sbert"),
        EMBED_DEVICE=_env("EMBED_DEVICE", "auto"),
        DEFAULT_TOP_K=int(_env("DEFAULT_TOP_K", "5")),
    )

# để code cũ khỏi gãy: tạo biến settings global
settings = get_settings()

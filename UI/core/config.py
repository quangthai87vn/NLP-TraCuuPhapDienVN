# UI/core/config.py
import os
from dataclasses import dataclass
from pathlib import Path


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


def project_root() -> Path:
    # UI/core/config.py -> UI/core -> UI -> PROJECT_ROOT
    return Path(__file__).resolve().parents[2]


def abs_path(p: str) -> str:
    p = p.strip()
    if os.path.isabs(p):
        return p
    return str(project_root() / p)


def get_settings() -> Settings:
    return Settings(
        CSV_PATH=_env("CSV_PATH", "backend/rag/qna-sql/pdchude.csv"),
        CHROMA_DIR=_env("CHROMA_DIR", "UI/vector_db"),
        CHROMA_COLLECTION=_env("CHROMA_COLLECTION", "iuh_law_advisor_2026"),
        SQLITE_PATH=_env("SQLITE_PATH", "UI/data/ui.sqlite3"),
        EMBED_MODEL_ID=_env("EMBED_MODEL_ID", "keepitreal/vietnamese-sbert"),
        EMBED_DEVICE=_env("EMBED_DEVICE", "auto"),
        DEFAULT_TOP_K=int(_env("DEFAULT_TOP_K", "5")),
    )


# ✅ export sẵn để nơi khác import "settings"
settings = get_settings()

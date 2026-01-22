# UI/core/config.py
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

try:
    # nếu có python-dotenv thì auto load .env
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception:
    pass


# project_root = .../PROJECT (vì file nằm ở PROJECT/UI/core/config.py)
PROJECT_ROOT = Path(__file__).resolve().parents[2]


def abs_path(p: str | Path) -> Path:
    """
    Chuẩn hoá đường dẫn:
    - Nếu p là absolute => giữ nguyên
    - Nếu p là relative => hiểu theo PROJECT_ROOT (ổn định khi chạy streamlit ở mọi cwd)
    """
    pp = Path(p).expanduser()
    if pp.is_absolute():
        return pp
    return (PROJECT_ROOT / pp).resolve()


def _env(key: str, default: str) -> str:
    v = os.getenv(key, default)
    return v.strip() if isinstance(v, str) else default


@dataclass(frozen=True)
class Settings:
    CSV_PATH: str
    CHROMA_DIR: str
    CHROMA_COLLECTION: str
    SQLITE_PATH: str
    EMBED_MODEL_ID: str
    EMBED_DEVICE: str
    DEFAULT_TOP_K: int


def get_settings() -> Settings:
    return Settings(
        CSV_PATH=_env("CSV_PATH", "data/pdchude.csv"),
        CHROMA_DIR=_env("CHROMA_DIR", "UI/vector_db"),
        CHROMA_COLLECTION=_env("CHROMA_COLLECTION", "iuh_law_advisor_2026"),
        SQLITE_PATH=_env("SQLITE_PATH", "UI/data/ui.sqlite3"),
        EMBED_MODEL_ID=_env("EMBED_MODEL_ID", "keepitreal/vietnamese-sbert"),
        EMBED_DEVICE=_env("EMBED_DEVICE", "auto"),
        DEFAULT_TOP_K=int(_env("DEFAULT_TOP_K", "5")),
    )


# ✅ biến settings để các file khác import thẳng
settings = get_settings()

# (tuỳ bạn) expose constants kiểu cũ cho tương thích
CSV_PATH = settings.CSV_PATH
CHROMA_DIR = settings.CHROMA_DIR
CHROMA_COLLECTION = settings.CHROMA_COLLECTION
SQLITE_PATH = settings.SQLITE_PATH
EMBED_MODEL_ID = settings.EMBED_MODEL_ID
EMBED_DEVICE = settings.EMBED_DEVICE
DEFAULT_TOP_K = settings.DEFAULT_TOP_K

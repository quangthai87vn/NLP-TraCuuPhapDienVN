from __future__ import annotations

from pathlib import Path
import shutil

import streamlit as st


def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def download_hf_model(model_id: str, dst_dir: str) -> Path:
    """
    Download model snapshot into dst_dir/<safe_name>
    """
    from huggingface_hub import snapshot_download

    safe = model_id.replace("/", "__")
    root = Path(dst_dir).resolve()
    ensure_dir(root)
    target = root / safe
    ensure_dir(target)

    snapshot_download(
        repo_id=model_id,
        local_dir=str(target),
        local_dir_use_symlinks=False,
        resume_download=True,
    )
    return target

import re
import hashlib
from typing import List

def clean_text(s: str) -> str:
    if s is None:
        return ""
    s = str(s)
    s = s.replace("\u00a0", " ")
    s = re.sub(r"\s+", " ", s).strip()
    return s

def stable_id(*parts: str) -> str:
    h = hashlib.sha1()
    for p in parts:
        h.update(str(p).encode("utf-8", errors="ignore"))
        h.update(b"|")
    return h.hexdigest()

def chunk_text(text: str, chunk_size: int = 1500, chunk_overlap: int = 120) -> List[str]:
    text = clean_text(text)
    if not text:
        return []
    if chunk_size <= 0:
        return [text]

    chunks = []
    start = 0
    n = len(text)
    step = max(1, chunk_size - max(0, chunk_overlap))

    while start < n:
        end = min(n, start + chunk_size)
        chunks.append(text[start:end])
        if end == n:
            break
        start += step

    return chunks

def detect_device(mode: str = "auto") -> str:
    mode = (mode or "auto").lower().strip()
    if mode in ("cpu", "cuda"):
        return mode

    # auto
    try:
        import torch
        return "cuda" if torch.cuda.is_available() else "cpu"
    except Exception:
        return "cpu"

import os
import hashlib
from typing import Callable, Dict, Any, List, Optional

import torch
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings as ChromaSettings

from .csv_loader import load_law_docs_from_csv


def resolve_device(device_choice: str) -> str:
    device_choice = (device_choice or "auto").lower()
    if device_choice == "cpu":
        return "cpu"
    if device_choice == "cuda":
        return "cuda" if torch.cuda.is_available() else "cpu"
    return "cuda" if torch.cuda.is_available() else "cpu"


def device_status_text(device_real: str) -> str:
    if device_real == "cuda" and torch.cuda.is_available():
        name = torch.cuda.get_device_name(0)
        return f"✅ Đang dùng: CUDA ({name})"
    return "✅ Đang dùng: CPU"


def _chunk_text(text: str, chunk_size: int, overlap: int) -> List[str]:
    text = (text or "").strip()
    if not text:
        return []
    if chunk_size <= 0:
        return [text]

    chunks = []
    start = 0
    n = len(text)
    step = max(chunk_size - overlap, 1)

    while start < n:
        end = min(start + chunk_size, n)
        chunks.append(text[start:end])
        if end == n:
            break
        start += step
    return chunks


def _safe_hash(s: str, n: int = 12) -> str:
    return hashlib.md5((s or "").encode("utf-8")).hexdigest()[:n]


def run_embedding(
    csv_path: str,
    chroma_dir: str,
    collection: str,
    model_id: str,
    device: str,
    chunk_size: int = 1200,
    chunk_overlap: int = 120,
    batch_size: int = 128,
    on_progress: Optional[Callable[[int, int], None]] = None,
) -> Dict[str, Any]:
    """
    Build Chroma collection from a CSV file.
    - Fix DuplicateIDError bằng cách tạo id theo row_index + chunk_index + hash.
    - ChromaDB bản mới: KHÔNG cần client.persist() (auto-persist).
    """
    device_real = resolve_device(device)

    # Ensure persist dir
    os.makedirs(chroma_dir, exist_ok=True)

    # Persistent client (auto persist)
    client = chromadb.PersistentClient(
        path=chroma_dir,
        settings=ChromaSettings(anonymized_telemetry=False),
    )
    col = client.get_or_create_collection(name=collection)

    # Load docs
    docs = load_law_docs_from_csv(csv_path)

    ids: List[str] = []
    texts: List[str] = []
    metas: List[Dict[str, Any]] = []

    for row_idx, d in enumerate(docs):
        base_id = str(d.get("id", "")).strip() or f"row_{row_idx}"
        full_text = d.get("text", "") or ""
        chunks = _chunk_text(full_text, chunk_size, chunk_overlap)

        row_hash = _safe_hash(full_text)

        for chunk_idx, ch in enumerate(chunks):
            uid = f"{base_id}__r{row_idx}__c{chunk_idx}__{row_hash}"
            ids.append(uid)
            texts.append(ch)

            m = dict(d.get("meta", {}))
            m["source_id"] = base_id
            m["row_index"] = row_idx
            m["chunk_index"] = chunk_idx
            m["row_hash"] = row_hash
            metas.append(m)

    total_chunks = len(texts)
    total_rows = len(docs)

    if total_chunks == 0:
        return {"total_rows": total_rows, "total_chunks": 0}

    # Load embedding model
    model = SentenceTransformer(model_id, device=device_real)

    # Encode + upsert by batches
    done = 0
    for i in range(0, total_chunks, batch_size):
        batch_texts = texts[i : i + batch_size]
        batch_ids = ids[i : i + batch_size]
        batch_metas = metas[i : i + batch_size]

        # chống trùng trong batch (cực hiếm nhưng cứ chặn)
        seen = set()
        for k in range(len(batch_ids)):
            bid = batch_ids[k]
            if bid in seen:
                batch_ids[k] = f"{bid}__dup{k}"
            seen.add(batch_ids[k])

        emb = model.encode(
            batch_texts,
            batch_size=min(batch_size, 256),
            show_progress_bar=False,
            normalize_embeddings=True,
        )

        col.upsert(
            ids=batch_ids,
            documents=batch_texts,
            embeddings=emb,
            metadatas=batch_metas,
        )

        done = min(i + len(batch_texts), total_chunks)
        if on_progress:
            on_progress(done, total_chunks)

    # ✅ ChromaDB persistent client auto-save, không gọi persist nữa
    return {"total_rows": total_rows, "total_chunks": total_chunks}

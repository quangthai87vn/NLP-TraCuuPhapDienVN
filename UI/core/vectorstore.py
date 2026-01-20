# UI/core/vectorstore.py
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

import chromadb
from chromadb.config import Settings as ChromaSettings

from .config import settings, abs_path


@dataclass
class Hit:
    doc: str
    meta: Dict[str, Any]
    distance: float
    id: str  # vẫn giữ để dùng nếu Chroma trả ids


_embedder = None
_embedder_device = None


def _resolve_device(device: str) -> str:
    if device and device.lower() != "auto":
        return device.lower()
    try:
        import torch
        return "cuda" if torch.cuda.is_available() else "cpu"
    except Exception:
        return "cpu"


def _get_embedder():
    global _embedder, _embedder_device
    if _embedder is None:
        from sentence_transformers import SentenceTransformer
        _embedder_device = _resolve_device(settings.EMBED_DEVICE)
        _embedder = SentenceTransformer(settings.EMBED_MODEL_ID, device=_embedder_device)
    return _embedder


class ChromaStore:
    def __init__(self, persist_dir: str, collection_name: str):
        p = Path(abs_path(persist_dir))
        p.mkdir(parents=True, exist_ok=True)

        self.persist_dir = p
        self.collection_name = collection_name

        self.client = chromadb.PersistentClient(
            path=str(self.persist_dir),
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        self.col = self.client.get_or_create_collection(name=self.collection_name)

    def query(self, text: str, top_k: int = 5) -> List[Hit]:
        embedder = _get_embedder()
        vec = embedder.encode([text], normalize_embeddings=True).tolist()[0]

        # ✅ FIX: include KHÔNG được có "ids"
        res = self.col.query(
            query_embeddings=[vec],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )

        docs = (res.get("documents") or [[]])[0]
        metas = (res.get("metadatas") or [[]])[0]
        dists = (res.get("distances") or [[]])[0]

        # ids: tuỳ version chroma, có thể có hoặc không
        ids_list = res.get("ids")
        ids = (ids_list or [[]])[0] if isinstance(ids_list, list) else []

        hits: List[Hit] = []
        for i, (doc, meta, dist) in enumerate(zip(docs, metas, dists)):
            _id = ids[i] if i < len(ids) else str(i)
            hits.append(
                Hit(
                    doc=doc or "",
                    meta=meta or {},
                    distance=float(dist),
                    id=str(_id),
                )
            )
        return hits

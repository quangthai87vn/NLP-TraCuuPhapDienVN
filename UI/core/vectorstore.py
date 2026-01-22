# UI/core/vectorstore.py
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import chromadb

from .config import settings, abs_path


@dataclass
class Hit:
    id: str
    doc: str
    meta: Dict[str, Any]
    distance: float


class ChromaStore:
    def __init__(self, persist_dir: str | Path, collection_name: str):
        p = abs_path(persist_dir)
        p.mkdir(parents=True, exist_ok=True)

        # ✅ Chroma persistent client
        self.client = chromadb.PersistentClient(path=str(p))
        self.col = self.client.get_or_create_collection(name=collection_name)

        self._embedder = None

    def _get_embedder(self):
        if self._embedder is not None:
            return self._embedder

        # Lazy import để tránh load nặng khi chưa dùng
        try:
            from sentence_transformers import SentenceTransformer  # type: ignore
        except Exception as e:
            raise RuntimeError(
                "Thiếu thư viện sentence-transformers. Cài: pip install sentence-transformers"
            ) from e

        device = settings.EMBED_DEVICE
        if device == "auto":
            # ưu tiên cuda nếu có
            try:
                import torch  # type: ignore

                device = "cuda" if torch.cuda.is_available() else "cpu"
            except Exception:
                device = "cpu"

        self._embedder = SentenceTransformer(settings.EMBED_MODEL_ID, device=device)
        return self._embedder

    def embed_query(self, text: str) -> List[float]:
        model = self._get_embedder()
        vec = model.encode([text], normalize_embeddings=True)
        return vec[0].tolist()

    def query(self, question: str, top_k: int = 5) -> List[Hit]:
        q_emb = self.embed_query(question)

        # ✅ include KHÔNG được chứa "ids" (Chroma sẽ trả ids sẵn trong res["ids"])
        res = self.col.query(
            query_embeddings=[q_emb],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )

        ids = (res.get("ids") or [[]])[0]
        docs = (res.get("documents") or [[]])[0]
        metas = (res.get("metadatas") or [[]])[0]
        dists = (res.get("distances") or [[]])[0]

        hits: List[Hit] = []
        for i in range(len(ids)):
            hits.append(
                Hit(
                    id=str(ids[i]),
                    doc=str(docs[i] or ""),
                    meta=dict(metas[i] or {}),
                    distance=float(dists[i]),
                )
            )
        return hits

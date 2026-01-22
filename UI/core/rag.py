# UI/core/rag.py
from __future__ import annotations
from typing import Any, Dict, List, Tuple

from .config import settings
from .vectorstore import ChromaStore, Hit


def retrieve_topk(question: str, top_k: int = 5) -> List[Tuple[dict, float]]:
    store = ChromaStore(settings.CHROMA_DIR, settings.CHROMA_COLLECTION)
    hits: List[Hit] = store.query(question, top_k=top_k)

    out: List[Tuple[dict, float]] = []
    for h in hits:
        meta = dict(h.meta or {})
        meta["__doc__"] = h.doc
        meta["__id__"] = h.id
        out.append((meta, h.distance))
    return out


def _format_citation(meta: dict) -> str:
    dieu = meta.get("dieu_ten") or meta.get("dieu") or meta.get("ten") or meta.get("mapc") or ""
    vb = meta.get("vbqppl") or meta.get("vb") or ""
    link = meta.get("vbqppl_link") or meta.get("link") or ""
    bits = []
    if dieu:
        bits.append(str(dieu))
    if vb:
        bits.append(f"({vb})")
    if link:
        bits.append(str(link))
    return " ".join(bits).strip()


def answer_with_citations(question: str, top_k: int = 5) -> Dict[str, Any]:
    hits = retrieve_topk(question, top_k=top_k)

    if not hits:
        return {
            "answer": "Mình chưa tìm thấy điều/khoản phù hợp trong dữ liệu hiện có.",
            "hits": [],
        }

    best_meta, best_dist = hits[0]
    doc = (best_meta.get("__doc__", "") or "").strip()

    cite = _format_citation(best_meta)
    if doc:
        answer = f"{doc}\n\n**Trích dẫn:** {cite}"
    else:
        answer = f"**Trích dẫn:** {cite}"

    return {"answer": answer, "hits": hits}

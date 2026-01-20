# UI/core/rag.py
from __future__ import annotations
from typing import Any, Dict, List, Tuple

from .config import settings
from .vectorstore import ChromaStore


def retrieve_topk(question: str, top_k: int = 5) -> List[Tuple[dict, float]]:
    store = ChromaStore(settings.CHROMA_DIR, settings.CHROMA_COLLECTION)
    hits = store.query(question, top_k=top_k)

    out: List[Tuple[dict, float]] = []
    for h in hits:
        meta = dict(h.meta or {})
        meta["__doc__"] = h.doc or ""
        out.append((meta, float(h.distance)))
    return out


def _format_citation(meta: dict) -> str:
    # Ưu tiên trích dẫn dạng Điều/Khoản nếu có (tùy metadata lúc embedding)
    dieu = meta.get("dieu_ten") or meta.get("ten") or meta.get("mapc") or ""
    khoan = meta.get("khoan") or meta.get("khoan_so") or ""
    vb = meta.get("vbqppl") or meta.get("vb") or ""
    link = meta.get("vbqppl_link") or meta.get("link") or ""

    bits = []
    if dieu:
        bits.append(str(dieu))
    if khoan:
        bits.append(f"Khoản {khoan}")
    if vb:
        bits.append(f"({vb})")
    if link:
        bits.append(link)
    return " ".join(bits).strip()


def _build_followups(question: str) -> List[str]:
    q = (question or "").lower()

    # Heuristic đơn giản (không bịa luật)
    base = [
        "Bạn cho mình biết **bối cảnh cụ thể** (ai – làm gì – ở đâu – thời điểm nào) để mình đối chiếu đúng Điều/Khoản hơn được không?",
        "Trường hợp này có **giấy tờ/biên bản/quyết định** nào liên quan không (nếu có, nói tên/loại văn bản)?",
    ]

    if any(k in q for k in ["tai nạn", "va chạm", "tông", "đâm", "giao thông"]):
        return [
            "Bạn cho mình biết **loại phương tiện** + **hành vi vi phạm** cụ thể (vượt đèn đỏ/đi ngược chiều/không đội mũ...)?",
            "Sự việc xảy ra **ở tỉnh/thành nào** và có **CSGT lập biên bản** chưa?",
        ]
    if any(k in q for k in ["hợp đồng", "mua bán", "đặt cọc", "cho vay", "nợ"]):
        return [
            "Bạn cho mình biết **hợp đồng bằng miệng hay văn bản**? có chứng cứ gì (tin nhắn/chuyển khoản)?",
            "Bạn đang muốn hỏi về **quyền lợi**, **trách nhiệm**, hay **cách xử lý tranh chấp**?",
        ]

    return base


def answer_with_citations(question: str, top_k: int = 5) -> Dict[str, Any]:
    hits = retrieve_topk(question, top_k=top_k)

    if not hits:
        return {
            "answer": "Mình chưa tìm thấy Điều/Khoản phù hợp trong dữ liệu vector hiện có. Bạn thử diễn đạt lại câu hỏi cụ thể hơn (hành vi + bối cảnh) nhé.",
            "hits": [],
            "followups": _build_followups(question),
        }

    best_meta, best_dist = hits[0]
    doc = (best_meta.get("__doc__", "") or "").strip()
    cite = _format_citation(best_meta) or "(không thấy Điều/Khoản cụ thể trong dữ liệu truy xuất)"

    # Giới hạn độ dài để UI không “nổ tung”
    doc_show = doc
    if len(doc_show) > 1600:
        doc_show = doc_show[:1600].rstrip() + " ..."

    # “mượt” bằng format chuẩn
    answer_parts = []
    if doc_show:
        answer_parts.append(doc_show)
    answer_parts.append(f"\n**Trích dẫn:** {cite}")
    answer_parts.append("\n**Cần mình làm rõ nhanh 2 ý này nhé:**")
    for i, fu in enumerate(_build_followups(question), 1):
        answer_parts.append(f"- {fu}")

    return {
        "answer": "\n".join(answer_parts).strip(),
        "hits": hits,
    }

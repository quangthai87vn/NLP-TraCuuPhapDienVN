'''
import streamlit as st

# ✅ robust import settings (tránh lỗi "cannot import name settings")
try:
    from core.config import settings
except Exception:
    from core.config import get_settings
    settings = get_settings()

from core.db import init_db, add_chat_message, get_chat_messages, clear_chat
from core.rag import answer_with_citations, retrieve_topk

st.set_page_config(page_title="Chatbot", page_icon="💬", layout="wide")
init_db()

# ====== CSS: bubble + font + align ======
st.markdown(
    """
<style>
/* tăng font tổng */
html, body, [class*="css"]  { font-size: 18px; }

/* bubble */
.chat-bubble {
  padding: 12px 14px;
  border-radius: 16px;
  margin: 6px 0;
  line-height: 1.45;
  font-size: 18px;
  border: 1px solid rgba(49, 51, 63, 0.15);
  background: rgba(240, 242, 246, 0.85);
  white-space: pre-wrap;
}

/* bot (trái) */
.bubble-bot {
  border-top-left-radius: 6px;
}

/* user (phải) */
.bubble-user {
  border-top-right-radius: 6px;
  background: rgba(0, 122, 255, 0.10);
}

/* text nhỏ gợi ý sau câu trả lời */
.followup {
  margin-top: 10px;
  font-size: 14px;
  opacity: 0.8;
}
</style>
""",
    unsafe_allow_html=True,
)

st.markdown("# 💬 Chatbot (Trích dẫn Điều/Khoản)")
st.caption("✅ Chatbot bên trái • ✅ Người dùng bên phải • Có thể xem TopK từ VectorDB")

# ====== sidebar config ======
st.sidebar.subheader("⚙️ Cấu hình")
st.sidebar.write(f"**Embedding model:** `{getattr(settings, 'EMBED_MODEL_ID', 'N/A')}`")

top_k = st.sidebar.slider(
    "Top K",
    min_value=1,
    max_value=20,
    value=int(getattr(settings, "DEFAULT_TOP_K", 5)),
    step=1,
)

if st.sidebar.button("🧹 Xoá lịch sử chat"):
    clear_chat()
    st.rerun()

# ====== helper render bubble ======
def render_message(role: str, content: str):
    """
    role: 'user' or 'assistant'
    user -> right
    assistant -> left
    """
    left, right = st.columns([1, 1], gap="large")

    if role == "assistant":
        with left:
            st.markdown(
                f'<div class="chat-bubble bubble-bot">{content}</div>',
                unsafe_allow_html=True,
            )
        with right:
            st.write("")
    else:
        with left:
            st.write("")
        with right:
            st.markdown(
                f'<div class="chat-bubble bubble-user">{content}</div>',
                unsafe_allow_html=True,
            )

# ====== render history ======
history = get_chat_messages(limit=80)
for m in history:
    render_message(m["role"], m["content"])

# ====== chat input ======
q = st.chat_input("Nhập câu hỏi pháp luật... (Enter để gửi)")
if q:
    add_chat_message("user", q)
    render_message("user", q)

    # loading "đang suy nghĩ"
    with st.spinner("Chatbot đang suy nghĩ..."):
        out = answer_with_citations(q, top_k=top_k)

    bot_text = out.get("answer", "(Không có câu trả lời)")

    # ✅ gợi ý hỏi tiếp cho mượt (append vào cuối)
    followup = (
        "\n\n---\n"
        "💡 *Muốn mình trả lời sát hơn không?* Bạn cho mình thêm 1 trong các ý này nhé:\n"
        "- Tình huống cụ thể của bạn là gì (ai, làm gì, ở đâu, thời điểm nào)?\n"
        "- Bạn cần **trích Điều/Khoản** hay cần **mức phạt / thủ tục / quyền-nghĩa vụ**?\n"
        "- Nếu có tên văn bản/điều luật nghi ngờ, bạn gửi mình keyword (vd: “xe máy”, “hợp đồng”, “đất đai”, “ly hôn”)."
    )
    bot_full = bot_text + f'\n\n<div class="followup">{followup}</div>'

    add_chat_message("assistant", bot_text + followup)  # lưu luôn cả gợi ý để history đồng nhất
    render_message("assistant", bot_full)

    # ====== TopK viewer ======
    with st.expander("🔎 Xem TopK từ VectorDB"):
        hits = retrieve_topk(q, top_k=top_k)
        if not hits:
            st.info("Không thấy đoạn nào trong VectorDB (hoặc chưa build embedding).")
        else:
            for i, (meta, dist) in enumerate(hits, 1):
                st.markdown(f"**#{i}**  (distance={dist:.4f})")
                st.write(meta.get("dieu_ten", ""))
                st.write(meta.get("vbqppl", ""))
                if meta.get("vbqppl_link"):
                    st.write(meta["vbqppl_link"])
                st.divider()


'''

# UI/pages/1_Chatbot.py
from __future__ import annotations

import time
import streamlit as st

from core.config import settings
from core.db import init_db, add_chat_message, get_chat_messages, clear_chat_messages
from core.rag import answer_with_citations


# -------------------------
# CSS: user RIGHT, bot LEFT + font bigger
# -------------------------
CHAT_CSS = """
<style>
/* tăng font chat */
div[data-testid="stChatMessage"] {
  font-size: 1.05rem;
  line-height: 1.55;
}

/* canh user sang phải */
div[data-testid="stChatMessage"][data-role="user"] {
  flex-direction: row-reverse;
  text-align: right;
}
div[data-testid="stChatMessage"][data-role="user"] .stMarkdown {
  text-align: right;
}

/* canh assistant sang trái */
div[data-testid="stChatMessage"][data-role="assistant"] {
  flex-direction: row;
  text-align: left;
}
</style>
"""

DEFAULT_SYSTEM_PROMPT = """Bạn là “NLP - IUH Law Advisor 2026”, trợ lý hỏi đáp pháp luật Việt Nam.
Nhiệm vụ: trả lời dựa trên dữ liệu truy xuất (Top-K) từ hệ thống vector database.

QUY TẮC:
- Không bịa điều luật. Nếu dữ liệu không đủ, nói rõ và hỏi thêm.
- Neu dữ liệu truy xuất (Top-K) không liên quan, hãy thẳng thắn nói không biết.
- Ưu tiên trích dẫn “Điều/Khoản/Chương” nếu có trong dữ liệu.
- Trả lời ngắn gọn, dễ hiểu, và hỏi thêm tối đa 2 câu để làm rõ.
"""

DEFAULT_STYLE_PROMPT = """Phong cách: nói rõ ràng, gọn, ưu tiên bullet. Tránh lan man."""


def _render_topk(hits):
    if not hits:
        st.info("Top-K trống (chưa tìm thấy dữ liệu).")
        return

    # show từng hit
    for idx, (meta, dist) in enumerate(hits, 1):
        title = meta.get("dieu_ten") or meta.get("ten") or meta.get("mapc") or f"Hit #{idx}"
        vb = meta.get("vbqppl") or meta.get("vb") or ""
        link = meta.get("vbqppl_link") or meta.get("link") or ""
        snippet = (meta.get("__doc__", "") or "").strip()
        if len(snippet) > 600:
            snippet = snippet[:600].rstrip() + " ..."

        with st.expander(f"#{idx} • {title} • dist={dist:.4f} {f'• {vb}' if vb else ''}", expanded=(idx == 1)):
            if link:
                st.markdown(f"**Link:** {link}")
            if vb:
                st.markdown(f"**VBQPPL:** {vb}")
            st.markdown("**Đoạn trích:**")
            st.write(snippet if snippet else "(không có nội dung doc)")


def main():
    st.set_page_config(page_title="Chatbot | NLP - IUH Law Advisor 2026", page_icon="⚖️", layout="wide")
    st.markdown(CHAT_CSS, unsafe_allow_html=True)

    init_db()

    # session state
    if "system_prompt" not in st.session_state:
        st.session_state.system_prompt = DEFAULT_SYSTEM_PROMPT
    if "style_prompt" not in st.session_state:
        st.session_state.style_prompt = DEFAULT_STYLE_PROMPT
    if "show_topk" not in st.session_state:
        st.session_state.show_topk = True
    if "last_hits" not in st.session_state:
        st.session_state.last_hits = []

    st.title("💬 Chatbot – Hỏi đáp Pháp Luật")
    st.caption("Trả lời dựa trên dữ liệu vector (Chroma). Ưu tiên trích dẫn Điều/Khoản nếu có.")

    # sidebar controls
    st.sidebar.markdown("### ⚙️ Cấu hình")
    top_k = st.sidebar.slider("Top-K truy xuất", 1, 10, int(settings.DEFAULT_TOP_K))
    st.session_state.show_topk = st.sidebar.toggle("Luôn hiển thị Top-K", value=st.session_state.show_topk)

    colA, colB = st.sidebar.columns(2)
    with colA:
        if st.button("🧹 Xoá lịch sử"):
            clear_chat_messages()
            st.session_state.last_hits = []
            st.rerun()
    with colB:
        if st.button("↩️ Reset Prompt"):
            st.session_state.system_prompt = DEFAULT_SYSTEM_PROMPT
            st.session_state.style_prompt = DEFAULT_STYLE_PROMPT
            st.rerun()

    st.sidebar.markdown("### 🧠 Prompt (để mượt hơn)")
    st.session_state.system_prompt = st.sidebar.text_area("System Prompt", st.session_state.system_prompt, height=180)
    st.session_state.style_prompt = st.sidebar.text_area("Style Prompt", st.session_state.style_prompt, height=110)

    # load history from sqlite and render
    history = get_chat_messages(limit=200)
    for m in history:
        role = m.get("role", "assistant")
        content = m.get("content", "")
        with st.chat_message(role):
            st.markdown(content)

    # input
    q = st.chat_input("Nhập câu hỏi pháp luật của bạn… (Enter để gửi)")
    if q:
        # render user msg
        add_chat_message("user", q)
        with st.chat_message("user"):
            st.markdown(q)

        # answer
        with st.chat_message("assistant"):
            thinking = st.empty()
            start = time.time()
            # hiệu ứng “đang suy nghĩ” nhẹ
            for i in range(1, 4):
                thinking.caption(f"Chatbot đang suy nghĩ {i} giây…")
                time.sleep(0.25)
            out = answer_with_citations(q, top_k=top_k)
            thinking.empty()

            answer = out.get("answer", "")
            hits = out.get("hits", [])
            st.session_state.last_hits = hits

            st.markdown(answer)

            # Top-K ngay dưới câu trả lời
            if st.session_state.show_topk:
                st.markdown("---")
                st.subheader("🔎 Top-K (để kiểm tra dữ liệu)")
                _render_topk(hits)

            took = time.time() - start
            st.caption(f"⏱️ xử lý: {took:.2f}s")

        add_chat_message("assistant", answer)
        st.rerun()

    # Nếu không hỏi gì, vẫn cho xem Top-K của câu gần nhất (tuỳ chọn)
    if st.session_state.show_topk and st.session_state.last_hits:
        st.markdown("---")
        st.subheader("🔎 Top-K của câu gần nhất")
        _render_topk(st.session_state.last_hits)


if __name__ == "__main__":
    main()

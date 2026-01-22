# UI/pages/1_Chatbot.py
from __future__ import annotations

import streamlit as st

from core.config import settings
from core.rag import answer_with_citations


st.set_page_config(page_title="Chatbot (Trích dẫn Điều/Khoản)", layout="wide")

# ✅ CSS cho chữ to hơn + đẹp hơn
st.markdown(
    """
<style>
/* tăng size chat */
.stChatMessage { font-size: 18px; line-height: 1.55; }
.stMarkdown, .stText, p, li { font-size: 18px !important; }

/* input to hơn */
textarea, input { font-size: 18px !important; }
</style>
""",
    unsafe_allow_html=True,
)

st.title("💬 Chatbot (Trích dẫn Điều/Khoản)")
st.caption("User bên phải, Bot bên trái. Có thể bật Top-K để kiểm tra dữ liệu lấy từ VectorDB.")


# ============== SIDEBAR ==============
with st.sidebar:
    st.header("⚙️ Cấu hình")

    st.write("**Embedding model:**", settings.EMBED_MODEL_ID)
    top_k = st.slider("Top K", min_value=1, max_value=20, value=int(settings.DEFAULT_TOP_K), step=1)

    show_topk = st.checkbox("Hiển thị Top-K (debug)", value=True)

    default_prompt = (
        "Bạn là trợ lý pháp lý tiếng Việt.\n"
        "Nhiệm vụ: trả lời NGẮN GỌN, dễ hiểu, đúng trọng tâm dựa trên đoạn luật được truy xuất.\n"
        "Luôn kèm 'Trích dẫn: ...' (Điều/Khoản/VB nếu có).\n"
        "Nếu câu hỏi mơ hồ, hãy hỏi lại 1 câu để làm rõ (mượt, tự nhiên).\n"
        "Không bịa nội dung ngoài dữ liệu."
    )
    sys_prompt = st.text_area("System Prompt (tuỳ chỉnh)", value=default_prompt, height=220)

# ============== SESSION STATE ==============
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Bạn hỏi mình về luật gì nè? (ví dụ: mức phạt vượt đèn đỏ, thủ tục công chứng, ...)"}
    ]

# render history
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# ============== CHAT INPUT ==============
q = st.chat_input("Nhập câu hỏi…")
if q:
    st.session_state.messages.append({"role": "user", "content": q})
    with st.chat_message("user"):
        st.markdown(q)

    with st.chat_message("assistant"):
        # 🔥 gọi RAG
        out = answer_with_citations(q, top_k=top_k)
        ans = out["answer"]

        # Mượt hơn: nếu sys_prompt muốn “hỏi lại”, bạn tự thêm 1 câu follow-up nhẹ
        # (vì hiện tại rag.py đang trả doc top1, chưa gọi LLM)
        follow_up = "\n\nNếu bạn nói rõ **bối cảnh** (tỉnh/thành, hành vi cụ thể, thời điểm…), mình trích đúng điều/khoản nhanh hơn."
        st.markdown(ans + follow_up)

        # debug Top-K
        if show_topk:
            hits = out.get("hits", [])
            with st.expander(f"Top-{len(hits)} hits (VectorDB)", expanded=False):
                for i, (meta, dist) in enumerate(hits, start=1):
                    doc = (meta.get("__doc__") or "")[:400]
                    st.markdown(f"**#{i}** | distance: `{dist:.4f}` | id: `{meta.get('__id__','')}`")
                    st.caption(doc)

    st.session_state.messages.append({"role": "assistant", "content": ans})

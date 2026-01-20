import streamlit as st
import pandas as pd

st.set_page_config(page_title="Evaluate", page_icon="📏", layout="wide")

st.markdown("## 📏 Evaluate")
st.caption("Gợi ý tiêu chí đánh giá RAG (retrieval + answer).")

st.markdown("### Tiêu chí gợi ý")
st.write("- **Precision@k, Recall@k** (đánh giá retrieval đúng tài liệu).")
st.write("- **MRR** (đúng tài liệu càng lên top càng tốt).")
st.write("- **nDCG** (có trọng số theo thứ hạng).")
st.write("- **Faithfulness / Citation correctness**: câu trả lời bám đúng trích dẫn Điều/Khoản (không bịa).")

st.markdown("### Dataset đánh giá")
st.info("Bạn có thể tạo file test dạng: question, relevant_dieu_id (hoặc relevant_text), và chạy batch query để tính metric.")

st.markdown("### Kết quả")
st.warning("Trang Evaluate bạn sẽ bổ sung sau. Nếu bạn gửi format bộ test (CSV), mình code luôn phần tính metric + báo cáo bảng/biểu đồ.")

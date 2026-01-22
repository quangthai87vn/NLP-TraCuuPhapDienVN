# UI/pages/2_Data_Source.py
import os
from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Data Source", layout="wide")
st.title("📚 Data Source")
st.caption("Load CSV trực tiếp từ biến môi trường CSV_PATH")

CSV_PATH = os.getenv("CSV_PATH", "").strip()

st.sidebar.subheader("⚙️ Cấu hình")
st.sidebar.text_input("CSV_PATH", value=CSV_PATH, disabled=True)

if not CSV_PATH:
    st.error("❌ Chưa có biến môi trường CSV_PATH. Hãy set CSV_PATH trong .env hoặc export trước khi chạy.")
    st.stop()

csv_file = Path(CSV_PATH)
if not csv_file.exists():
    st.error(f"❌ Không tìm thấy file CSV: {csv_file}")
    st.stop()

@st.cache_data(show_spinner=False)
def load_csv(p: str) -> pd.DataFrame:
    # tip: nếu CSV bạn có encoding khác thì đổi utf-8-sig -> utf-8 / cp1258
    return pd.read_csv(p, encoding="utf-8-sig")

with st.spinner("Đang load CSV..."):
    df = load_csv(str(csv_file))

st.success(f"✅ Loaded: {csv_file.name} | Rows: {len(df):,} | Cols: {len(df.columns)}")

# Bộ lọc đơn giản
with st.expander("🔎 Lọc nhanh", expanded=False):
    cols = list(df.columns)
    key_col = st.selectbox("Chọn cột để search", cols, index=0)
    q = st.text_input("Nhập từ khóa", "")
    limit = st.slider("Số dòng hiển thị", 50, 2000, 200, 50)

    if q.strip():
        mask = df[key_col].astype(str).str.contains(q, case=False, na=False)
        view = df[mask].head(limit)
    else:
        view = df.head(limit)

st.dataframe(view, use_container_width=True)

# Cho tải lại cache nếu muốn
if st.button("🔄 Reload CSV (clear cache)"):
    st.cache_data.clear()
    st.rerun()

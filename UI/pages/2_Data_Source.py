# UI/pages/2_Data_Source.py
import pandas as pd
import streamlit as st
from pathlib import Path

st.set_page_config(page_title="Data Source", page_icon="📚", layout="wide")

# ===== helpers =====
def find_root(start: Path) -> Path:
    cur = start.resolve()
    for _ in range(12):
        if (cur / "backend").exists() and (cur / "law-crawler").exists() and (cur / "UI").exists():
            return cur
        cur = cur.parent
    return start.resolve()

def as_file_uri(p: Path) -> str:
    return p.resolve().as_uri()

def read_csv_auto(path: Path) -> pd.DataFrame:
    try:
        return pd.read_csv(path, encoding="utf-8")
    except Exception:
        return pd.read_csv(path, encoding="latin1")

# ===== paths =====
ROOT = find_root(Path(__file__).parent)
HTML_PATH = ROOT / "law-crawler" / "phap dien" / "BoPhapDien.html"
CSV_PATH  = ROOT / "backend" / "rag" / "qna-sql" / "pdchude.csv"

# ===== UI (simple) =====
st.markdown("## 📚 Data Source")

# --- Top: one button only ---
col_btn = st.columns([1])[0]
with col_btn:
    if HTML_PATH.exists():
        url = as_file_uri(HTML_PATH)
        try:
            st.link_button("🌐 XEM DỮ LIỆU PHÁP ĐIỂN TỪ CỔNG THÔNG TIN", url, use_container_width=True)
        except Exception:
            st.markdown(
                f'<a href="{url}" target="_blank" rel="noopener noreferrer">'
                f'<button style="width:100%;padding:10px 14px;border-radius:10px;'
                f'border:1px solid #ddd;cursor:pointer;">'
                f'🌐 Mở BoPhapDien.html</button></a>',
                unsafe_allow_html=True,
            )
    else:
        st.error("Không thấy BoPhapDien.html")
        st.code(str(HTML_PATH), language="text")

st.write("")  # spacing

# --- Bottom: Grid full width ---
if not CSV_PATH.exists():
    st.error("Không thấy pdchude.csv")
    st.code(str(CSV_PATH), language="text")
    st.stop()

df = read_csv_auto(CSV_PATH)

# Gridview chiếm hết trang: tăng height tuỳ bạn, mình set 740 cho đã mắt
st.dataframe(df, use_container_width=True, height=740)

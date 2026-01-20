# UI/pages/2_Data_Source.py
import pandas as pd
import streamlit as st
from pathlib import Path

st.set_page_config(page_title="Data Source", page_icon="📚", layout="wide")

# ---- load settings (tương thích cả trường hợp bạn đổi config.py) ----
try:
    from core.config import settings  # nếu bạn có settings = get_settings()
except Exception:
    from core.config import get_settings
    settings = get_settings()

# ---- helpers ----
def read_csv_auto(path: Path) -> pd.DataFrame:
    try:
        return pd.read_csv(path, encoding="utf-8")
    except Exception:
        return pd.read_csv(path, encoding="latin1")

# Repo root = .../RAG-TraCuuPhapLuatVN
# pages/2_Data_Source.py -> parents[0]=pages, [1]=UI, [2]=root
ROOT = Path(__file__).resolve().parents[2]

# Lấy CSV_PATH từ .env (thông qua settings)
csv_raw = getattr(settings, "CSV_PATH", None) or ""
if not csv_raw.strip():
    st.error("❌ CSV_PATH đang rỗng. Hãy set trong file .env (ở thư mục gốc).")
    st.stop()

csv_path = Path(csv_raw)

# Nếu CSV_PATH là đường dẫn tương đối -> hiểu theo root project
if not csv_path.is_absolute():
    csv_path = (ROOT / csv_path).resolve()

st.markdown("## 📚 Data Source")
st.caption(f"CSV_PATH = `{csv_path}`")

if not csv_path.exists():
    st.error("❌ Không tìm thấy file CSV theo CSV_PATH.")
    st.code(str(csv_path), language="text")
    st.stop()

df = read_csv_auto(csv_path)
st.dataframe(df, use_container_width=True, height=740)

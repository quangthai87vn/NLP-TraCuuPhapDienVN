import streamlit as st
from pathlib import Path

UI_DIR = Path(__file__).parent
ASSETS = UI_DIR / "assets"

st.set_page_config(page_title="NLP - IUH Law Advisor 2026", layout="wide")




# UI/app.py (thêm lên đầu file)
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())



# Load CSS
css_path = ASSETS / "styles.css"
if css_path.exists():
    st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

# ===== Top bar (giống web) =====
st.markdown(
    """
    <div class="topbar">
      <div class="brand">NLP - IUH Law Advisor 2026</div>
      <div class="nav">
        <a href="#">Trang chủ</a>
        <a href="#">Pháp điển</a>
        <a href="#">VBQPPL</a>
        <a href="#">Đăng nhập</a>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ===== Hero banner =====
# Placeholder image (bạn thay bằng ảnh local sau: UI/assets/hero.png)
HERO_IMG = "https://phapdien.moj.gov.vn/qt/tintuc/PublishingImages/e704afb41f03e55dbc12.jpg"
st.markdown('<div class="hero"><div class="hero-inner">', unsafe_allow_html=True)
cL, cR = st.columns([0.95, 1.25], gap="large")

with cL:
    st.markdown('<div class="hero-left">', unsafe_allow_html=True)
    st.image(HERO_IMG, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with cR:
    st.markdown('<div class="hero-right">', unsafe_allow_html=True)
    st.markdown('<div class="hero-title">NLP - IUH Law Advisor 2026</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Hệ thống hỏi đáp tri thức pháp luật Việt Nam</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <ul class="hero-bullets">
          <li>Dựa trên mô hình ngôn ngữ lớn.</li>
          <li>Tri thức từ pháp điển Việt Nam và các VBQPPL.</li>
        </ul>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("</div></div>", unsafe_allow_html=True)

# ===== Search section =====
st.markdown('<div class="section-title">Tìm văn bản pháp luật bằng từ khóa</div>', unsafe_allow_html=True)

st.markdown('<div class="search-wrap"><div class="search-inner">', unsafe_allow_html=True)
scol1, scol2 = st.columns([12, 2], gap="small")
with scol1:
    keyword = st.text_input("", placeholder="Tìm một từ khóa...", label_visibility="collapsed", key="home_search")
with scol2:
    do_search = st.button("🔍", key="home_search_btn")
st.markdown("</div></div>", unsafe_allow_html=True)

if do_search and keyword.strip():
    st.info(f"Bạn vừa tìm: **{keyword}** (mình sẽ nối qua Data Source / Law API sau).")

# ===== Featured section =====
st.markdown('<div class="feature-title">Nổi Bật</div>', unsafe_allow_html=True)

# Placeholder images for cards (bạn thay sau)
IMG_CHAT = "https://img.freepik.com/vector-mien-phi/vectorart-cuoc-tro-chuyen-chatbot_78370-4107.jpg?semt=ais_hybrid&w=740&q=80"
IMG_PD   = "https://cdn.thuvienphapluat.vn/uploads/tintuc/2022/09/29/phap-dien.jpeg"
IMG_VB   = "https://cdn.luatvietnam.vn/uploaded/Images/Original/2021/06/01/kiem-tra-trung-ten-ho-kinh-doanh_0106154527.jpeg"
IMG_EVAL = "https://taxi123.com.vn/wp-content/uploads/2019/12/ava-gop-y.png"

cols = st.columns(4, gap="large")

def render_card(col, title, img, desc, btn_key, target_page=None, disabled=False):
    with col:
     
        st.markdown(f"<h4>{title}</h4>", unsafe_allow_html=True)
        st.markdown(f'<div class="card-img"><img src="{img}"/></div>', unsafe_allow_html=True)
        st.markdown(f"<p>{desc}</p>", unsafe_allow_html=True)
        clicked = st.button("Truy cập", key=btn_key, disabled=disabled)
        st.markdown("</div>", unsafe_allow_html=True)

        if clicked and target_page:
            st.switch_page(target_page)

render_card(
    cols[0],
    "Hỏi đáp Pháp Luật",
    IMG_CHAT,
    "Trợ lý AI giải đáp các câu hỏi về pháp luật Việt Nam.",
    "btn_home_chat",
    target_page="pages/1_Chatbot.py",
)

render_card(
    cols[1],
    "Tra cứu Pháp Điển",
    IMG_PD,
    "Tra cứu Pháp Điển Việt Nam hiện hành.",
    "btn_home_data",
    target_page="pages/2_Data_Source.py",
)

render_card(
    cols[2],
    "Tra cứu các VBQPPL",
    IMG_VB,
    "Tra cứu các điều luật từ VBQPPL Việt Nam.",
    "btn_home_vbqppl",
    target_page=None,
    disabled=True,
)


render_card(
    cols[3],
    "Đánh giá, góp ý",
    IMG_EVAL,
    "Đánh giá chất lượng truy hồi và góp ý hệ thống.",
    "btn_home_eval",
    target_page="pages/4_Evaluate.py",
)

st.markdown('<div class="footer">© IUH - GPL V3 License - 2026</div>', unsafe_allow_html=True)

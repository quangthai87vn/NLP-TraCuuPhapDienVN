

import os

import time



import streamlit as st

from core.config import get_settings
from core.db import (
    init_db,
    start_embedding_run,
    finish_embedding_run,
    get_embedding_logs,
)
from core.embedding_runner import run_embedding, resolve_device, device_status_text


st.set_page_config(page_title="Embedding", layout="wide")
init_db()

settings = get_settings()

st.title("🧠 Embedding → Chroma VectorDB")
st.caption("CSV → chunking → embedding → upsert vào Chroma (persist trong UI/).")

# ===== Sidebar controls =====
with st.sidebar:
    st.header("⚙️ Tham số")

    csv_path = st.text_input("CSV_PATH", value=settings.CSV_PATH)
    chroma_dir = st.text_input("CHROMA_DIR", value=settings.CHROMA_DIR)
    collection = st.text_input("Collection", value=settings.CHROMA_COLLECTION)

    model_id = st.text_input("Embedding model", value=settings.EMBED_MODEL_ID)

    device_choice = st.selectbox(
        "Device",
        options=["auto", "cuda", "cpu"],
        index=["auto", "cuda", "cpu"].index(settings.EMBED_DEVICE),
        help="auto: nếu có CUDA thì dùng CUDA, không có thì CPU",
    )

    st.markdown("---")
    chunk_size = st.slider("chunk_size", 200, 2000, 1200, step=50)
    chunk_overlap = st.slider("chunk_overlap", 0, 300, 120, step=10)
    batch_size = st.slider("batch_size", 8, 512, 128, step=8)

    # status
    device_real = resolve_device(device_choice)
    st.success(device_status_text(device_real))

# ===== Main actions =====
colA, colB = st.columns([1, 1], gap="large")

with colA:
    st.subheader("🚀 Chạy Embedding")
 

    # show resolved absolute paths (for sanity)
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    csv_abs = csv_path if os.path.isabs(csv_path) else os.path.join(project_root, csv_path)
    chroma_abs = chroma_dir if os.path.isabs(chroma_dir) else os.path.join(project_root, chroma_dir)

    st.code(
        f"CSV:     {csv_abs}\nCHROMA:   {chroma_abs}\nCOLLECT:  {collection}\nMODEL:    {model_id}\nDEVICE:   {device_real}",
        language="text",
    )

    run_btn = st.button("▶️ Chạy Embedding & Lưu VectorDB", type="primary", use_container_width=True)

with colB:
    st.subheader("🧾 Lịch sử")
    logs = get_embedding_logs(limit=20)
    if not logs:
        st.info("Chưa có lịch sử. Bấm chạy embedding để tạo log.")
    else:
        for r in logs:
            st.markdown(
                f"- **#{r['id']}** | {r.get('status','')} | "
                f"{r.get('started_at','')} → {r.get('finished_at','')} | "
                f"rows={r.get('total_rows','')} chunks={r.get('total_chunks','')} | "
                f"device={r.get('device','')} | note={r.get('note','')}"
            )

# ===== Execute embedding =====
from pathlib import Path
st.write("CSV exists:", Path(csv_path).exists(), "->", csv_path)



if run_btn:
    t0 = time.time()
    run_id = None
    try:
        run_id = start_embedding_run(
            model_id=model_id,
            device=device_real,
            chroma_dir=chroma_abs,
            collection=collection,
        )

        progress = st.progress(0, text="Đang chạy embedding...")

        def on_progress(done: int, total: int):
            pct = int((done / max(total, 1)) * 100)
            progress.progress(pct, text=f"Embedding: {done}/{total} chunks ({pct}%)")

        result = run_embedding(
            csv_path=csv_abs,
            chroma_dir=chroma_abs,
            collection=collection,
            model_id=model_id,
            device=device_real,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            batch_size=batch_size,
            on_progress=on_progress,
        )

        finish_embedding_run(
            run_id=run_id,
            status="ok",
            note=f"OK | time={time.time()-t0:.2f}s",
            total_rows=result["total_rows"],
            total_chunks=result["total_chunks"],
        )
        st.success(f"✅ Xong! rows={result['total_rows']} | chunks={result['total_chunks']} | time={time.time()-t0:.2f}s")

    except Exception as e:
        if run_id is not None:
            finish_embedding_run(run_id=run_id, status="failed", note=str(e))
        st.error(f"❌ Lỗi: {e}")
        st.exception(e)

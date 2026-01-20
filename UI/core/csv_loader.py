import os
import pandas as pd
from typing import List, Dict, Any


def load_law_docs_from_csv(csv_path: str) -> List[Dict[str, Any]]:
    """
    Chuẩn hóa output thành list dict:
    {
      "id": "...",
      "text": "...",        # nội dung để embed
      "meta": {...}         # metadata để trace
    }
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    df = pd.read_csv(csv_path)
    # bạn có thể tùy biến mapping theo CSV của bạn
    # ưu tiên các cột hay gặp
    col_id = "dieu_id" if "dieu_id" in df.columns else None
    col_title = "dieu_ten" if "dieu_ten" in df.columns else None
    col_text = "dieu_noidung" if "dieu_noidung" in df.columns else None
    col_src = "vbqppl" if "vbqppl" in df.columns else None
    col_link = "vbqppl_link" if "vbqppl_link" in df.columns else None

    docs = []
    for idx, row in df.iterrows():
        _id = str(row[col_id]) if col_id else str(idx)
        title = str(row[col_title]) if col_title else ""
        body = str(row[col_text]) if col_text else str(row.to_dict())

        text = (title.strip() + "\n" + body.strip()).strip()
        meta = {}
        if col_title: meta["dieu_ten"] = title
        if col_src: meta["vbqppl"] = str(row[col_src])
        if col_link: meta["vbqppl_link"] = str(row[col_link])
        meta["row_index"] = int(idx)

        docs.append({"id": _id, "text": text, "meta": meta})
    return docs

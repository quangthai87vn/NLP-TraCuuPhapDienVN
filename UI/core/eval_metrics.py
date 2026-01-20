from __future__ import annotations
from typing import List, Dict, Any, Tuple

def precision_at_k(pred_ids: List[str], gold_id: str, k: int) -> float:
    pred_k = pred_ids[:k]
    return 1.0 if gold_id in pred_k else 0.0

def recall_at_k(pred_ids: List[str], gold_id: str, k: int) -> float:
    # single gold item
    return 1.0 if gold_id in pred_ids[:k] else 0.0

def mrr(pred_ids: List[str], gold_id: str) -> float:
    for i, pid in enumerate(pred_ids, start=1):
        if pid == gold_id:
            return 1.0 / i
    return 0.0

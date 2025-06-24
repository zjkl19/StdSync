# ==================== stdsync/core/comparer.py =============
"""
comparer.py
比对算法：精准匹配 + 模糊匹配 + 状态判定
"""
from __future__ import annotations

import re
import unicodedata
from typing import List

import pandas as pd
from rapidfuzz import fuzz

from .models import CompanyStandard, MatchResult

# 相似度阈值
SIMILARITY_LOW, SIMILARITY_HIGH = 80, 90


# ----------------------------------------------------------------------
# 编号规范化：Unicode NFKC + 破折号统一
# ----------------------------------------------------------------------
def normalize_code(code: str) -> str:
    """
    将标准号统一为可比较的形式：
    1) Unicode NFKC 规范化（全角 → 半角）
    2) 将所有破折号 “-”“–” 归一为 “—”
    3) 去首尾空格
    """
    if code is None:
        return ""

    code = unicodedata.normalize("NFKC", str(code))
    code = re.sub(r"[-–]", "—", code)  # 半角连字符或短破折号 → 长破折号
    return code.strip()


# ----------------------------------------------------------------------
# 主对照函数
# ----------------------------------------------------------------------
def compare(company_df: pd.DataFrame, gb_df: pd.DataFrame) -> List[MatchResult]:
    """返回 MatchResult 列表"""

    # 构建 “旧号 → 新号” 映射
    replaced_map: dict[str, str] = {}
    for _, row in gb_df.iterrows():
        if pd.notna(row.get("replaced")):
            for old in re.split(r"[;；,，]", str(row["replaced"])):
                old_n = normalize_code(old)
                if old_n:
                    replaced_map[old_n] = normalize_code(row["code"])

    # 遍历公司标准
    results: List[MatchResult] = []
    for _, c in company_df.iterrows():
        cs = CompanyStandard(
            code=normalize_code(c["code"]),
            name=str(c["name"]),
            impl_date=None,
        )

        # 精确命中旧号
        if cs.code in replaced_map:
            results.append(
                MatchResult(
                    company=cs,
                    gb_old_code=cs.code,
                    gb_new_code=replaced_map[cs.code],
                    status="OBSOLETE",
                    similarity=100,
                    reason="精确命中旧号",
                )
            )
            continue

        # 名称模糊匹配
        best_score, best_code = 0, None
        for _, row in gb_df.iterrows():
            score = fuzz.token_set_ratio(cs.name, row["name"])
            if score > best_score:
                best_score, best_code = score, normalize_code(row["code"])

        if SIMILARITY_LOW <= best_score < SIMILARITY_HIGH:
            results.append(
                MatchResult(
                    company=cs,
                    gb_old_code=None,
                    gb_new_code=best_code,
                    status="REVIEW",
                    similarity=best_score,
                    reason=f"名称相似({best_score})",
                )
            )
        else:
            results.append(
                MatchResult(
                    company=cs,
                    gb_old_code=None,
                    gb_new_code=None,
                    status="OK",
                    similarity=best_score,
                )
            )

    return results

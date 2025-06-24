# ==================== stdsync/core/comparer.py ==================
"""
comparer.py  v0.2.0
---------------------------------------------------------------
规则：
1. 若公司旧号精确出现在公告 "replaced" 列 → OBSOLETE
2. 否则，若同时满足
      (a) 公司旧号与公告旧号字符串相似度 80–99
      (b) 名称相似度 ≥ 80
   → REVIEW
3. 其余 → OK
"""

from __future__ import annotations

import re
import unicodedata
from typing import List

import pandas as pd
from rapidfuzz import fuzz

from .models import CompanyStandard, MatchResult

# ------------------------------------------------------------------
# 编号规范化
# ------------------------------------------------------------------
def normalize_code(code: str) -> str:
    """
    全角→半角 + 统一破折号 → 去首尾空格
    """
    if code is None:
        return ""
    code = unicodedata.normalize("NFKC", str(code))
    code = re.sub(r"[-–]", "—", code)  # 半角或短破折号 → 长破折号
    return code.strip()


# ------------------------------------------------------------------
# 主对照函数
# ------------------------------------------------------------------
def compare(company_df: pd.DataFrame, gb_df: pd.DataFrame) -> List[MatchResult]:
    results: List[MatchResult] = []

    # 1) 构建旧→新映射（精确替代）
    replaced_map: dict[str, str] = {}
    for _, row in gb_df.iterrows():
        rep = row.get("replaced")
        if pd.isna(rep):
            continue
        for old in re.split(r"[;；,，]", str(rep)):
            old_n = normalize_code(old)
            if old_n:
                replaced_map[old_n] = normalize_code(row["code"])

    # 2) 遍历公司标准
    for _, c in company_df.iterrows():
        comp_code = normalize_code(c["code"])
        comp_name = str(c["name"])
        cs = CompanyStandard(code=comp_code, name=comp_name, impl_date=None)

        # ------- OBSOLETE -------------------------------------------------
        if comp_code in replaced_map:
            results.append(
                MatchResult(cs, comp_code, replaced_map[comp_code],
                            "OBSOLETE", 100, "精确命中旧号")
            )
            continue

        # ------- REVIEW 判定 ----------------------------------------------
        review_hit = None
        best_combo_score = 0  # 同时记录“编号+名称”的综合分

        for _, row in gb_df.iterrows():
            rep = row.get("replaced")
            if pd.isna(rep):
                continue  # 无旧号 → 不参与 REVIEW

            # 遍历公告旧号，找与公司编号最相似的一条
            code_score_max = 0
            for old in re.split(r"[;；,，]", str(rep)):
                old_norm = normalize_code(old)
                code_score = fuzz.ratio(comp_code, old_norm)
                code_score_max = max(code_score_max, code_score)

            if not (85 <= code_score_max < 100):      # 编号相似度未达 85~99
                continue

            # 计算名称相似度
            name_score = fuzz.token_set_ratio(comp_name, row["name"])
            if name_score < 85:                       # 名称相似度不足
                continue

            # 记录最佳组合（可选）
            combo_score = (code_score_max + name_score) / 2
            if combo_score > best_combo_score:
                best_combo_score = combo_score
                review_hit = normalize_code(row["code"])

        # ---------------- 结果输出 ----------------
        if review_hit:
            results.append(
                MatchResult(
                    cs, None, review_hit, "REVIEW",
                    int(best_combo_score),
                    f"编号{code_score_max}%, 名称{name_score}%"  # 备注
                )
            )
        else:
            results.append(
                MatchResult(cs, None, None, "OK",
                            fuzz.token_set_ratio(comp_name, comp_name))
            )
    return results

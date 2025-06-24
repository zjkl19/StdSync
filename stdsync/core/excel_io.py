# ==================== stdsync/core/excel_io.py =============
"""
excel_io.py
Excel 读写与数据清洗（支持装饰行、动态表头）
"""
from __future__ import annotations

import pandas as pd
import re
from pathlib import Path

# -----------------------------------------------------------
# 列名映射
# -----------------------------------------------------------
COL_MAP_COMPANY = {
    "标准编号": "code",
    "标准编号 ": "code",        # 末尾空格
    "标准名称": "name",
    "持有部门": "dept",
    "代替/修订情况": "replaced",
    "实施日期": "impl_date",
}
# 没有直接用到的列（忽略）
UNUSED_COMPANY_COLS = {"标准数量", "分发号1", "分发号2", "分发号3",
                       "分发号4", "分发号5", "分发号6", "分发号7",
                       "分发号8", "分发号9", "分发号10", "备注", "序号"}

COL_MAP_GB = {
    "国家标准编号": "code",
    "国 家 标 准 名 称": "name",
    "代替标准号": "replaced",
    "实施日期": "impl_date",
}

# 装饰行匹配
DECORATION_PATTERN = re.compile(r"部门在用标准清单")

# 标准编号有效性
VALID_CODE_PATTERN = re.compile(r"[A-Za-z0-9]")


# ----------------------------------------------------------------------
# 读取公司清单
# ----------------------------------------------------------------------
def _find_header_row(path: Path | str, sheet_name=0, max_scan=20) -> int:
    """
    扫描前 max_scan 行，找到包含“标准编号”的行号
    """
    tmp = pd.read_excel(path, sheet_name=sheet_name, header=None,
                        nrows=max_scan, dtype=str)
    for idx, row in tmp.iterrows():
        if row.astype(str).str.contains("标准编号").any():
            return idx
    raise ValueError("文件前 20 行未找到“标准编号”列，请检查格式")


def load_company(path: Path | str, sheet_name=0) -> pd.DataFrame:
    """
    读取并清洗公司标准清单
    * 自动跳过装饰首行
    * 自动定位表头
    * 重命名列 → code / name / dept / replaced / impl_date
    """
    path = Path(path)
    header_row = _find_header_row(path, sheet_name)

    # 第二次读取：指定 header 行
    df = pd.read_excel(path, sheet_name=sheet_name, header=header_row, dtype=str)

    # 去除装饰行（防止 header=0 时仍留下第一行）
    df = df[~df.iloc[:, 0].astype(str).str.match(DECORATION_PATTERN, na=False)]

    # 列名统一 strip → 半角
    df.rename(columns=lambda s: str(s).strip(), inplace=True)

    # 批量映射
    df.rename(columns=COL_MAP_COMPANY, inplace=True)

    # 删除不需要的列
    df.drop(columns=[c for c in df.columns if c in UNUSED_COMPANY_COLS],
            inplace=True, errors="ignore")

    # 缺列补空
    for col in ("code", "name", "dept", "replaced", "impl_date"):
        if col not in df.columns:
            df[col] = None

    # 过滤无效行
    df = df[df["code"].astype(str).str.match(VALID_CODE_PATTERN, na=False)]

    # 填充可能出现的合并单元格空值
    # 新写法（不触发链式赋值警告）
    df["code"] = df["code"].ffill()
    df["name"] = df["name"].ffill()

    return df.reset_index(drop=True)


# ----------------------------------------------------------------------
# 读取国家公告
# ----------------------------------------------------------------------
def load_gb(path: Path | str, sheet_name=0) -> pd.DataFrame:
    """
    读取国家标准公告（默认第一张表），并重命名列
    """
    df = pd.read_excel(path, sheet_name=sheet_name, dtype=str)
    df.rename(columns=lambda s: str(s).strip(), inplace=True)
    df.rename(columns=COL_MAP_GB, inplace=True, errors="ignore")

    # 缺列兜底
    for col in ("code", "name", "replaced", "impl_date"):
        if col not in df.columns:
            df[col] = None

    return df

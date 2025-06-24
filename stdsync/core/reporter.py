# ==================== stdsync/core/reporter.py ==================
"""
reporter.py – 生成差异报表（中文状态显示）
---------------------------------------------------------------
关键改动：
1. 英文状态 → 中文：已失效 / 待复核 / OK / 未使用
2. 条件格式匹配中文标签
3. append_trace() 同步写中文
"""
from __future__ import annotations

from pathlib import Path
from datetime import datetime
from typing import List

import xlsxwriter
import openpyxl

from .models import MatchResult

# 颜色映射
COLOR_MAP = {
    "已失效": "#FFC7CE",  # 红
    "待复核": "#FFEB9C",  # 黄 / 橙
    "OK":   "#C6EFCE",   # 绿
    "未使用": "#D9D9D9",  # 灰
}

# 英文 → 中文
STATUS_DISPLAY = {
    "OBSOLETE": "已失效",
    "REVIEW":   "待复核",
    "OK":       "OK",
    "UNUSED":   "未使用",
}

# 差异表列头
HEADERS = [
    "公司标准编号",
    "公司标准名称",
    "国家旧标准号",
    "国家新标准号",
    "实施日期",
    "状态",
    "相似度",
    "查找过程",
]

# ------------------------------------------------------------------
# 差异表输出
# ------------------------------------------------------------------

def render(results: List[MatchResult], out_path: Path | str) -> Path:
    out_path = Path(out_path)

    wb = xlsxwriter.Workbook(out_path)
    ws = wb.add_worksheet("差异表")
    hdr_fmt = wb.add_format({"bold": True, "bg_color": "#B7DEE8"})

    # 写表头
    for col, h in enumerate(HEADERS):
        ws.write(0, col, h, hdr_fmt)

    # 写数据行
    for r, m in enumerate(results, start=1):
        status_cn = STATUS_DISPLAY.get(m.status, m.status)
        ws.write_row(
            r,
            0,
            [
                m.company.code,
                m.company.name,
                m.gb_old_code,
                m.gb_new_code,
                "" if m.company.impl_date is None else str(m.company.impl_date),
                status_cn,
                m.similarity,
                m.reason,
            ],
        )

    # 条件格式着色（按中文标签）
    max_row = len(results)
    for status_cn, color in COLOR_MAP.items():
        ws.conditional_format(
            1,
            5,
            max_row,
            5,
            {
                "type": "cell",
                "criteria": "==",
                "value": f'"{status_cn}"',
                "format": wb.add_format({"bg_color": color}),
            },
        )

    wb.close()
    return out_path

# ------------------------------------------------------------------
# 在原国家公告文件追加“匹配状态”列
# ------------------------------------------------------------------

def append_trace(gb_path: Path | str, results: List[MatchResult]) -> None:
    gb_path = Path(gb_path)
    wb = openpyxl.load_workbook(gb_path)
    ws = wb.active

    # 新列标题
    col_idx = ws.max_column + 1
    ws.cell(row=1, column=col_idx).value = "匹配状态"

    # 公司标准编号 → 中文状态
    status_map = {m.company.code: STATUS_DISPLAY.get(m.status, m.status) for m in results}

    for r in range(2, ws.max_row + 1):
        std_code = ws.cell(row=r, column=1).value
        ws.cell(row=r, column=col_idx).value = status_map.get(std_code, "未使用")

    wb.save(gb_path.with_stem(gb_path.stem + "_trace"))

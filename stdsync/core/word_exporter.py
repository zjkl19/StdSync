# ==================== stdsync/core/word_exporter.py =======
"""Word 导出：仅导出已失效条目"""
from __future__ import annotations
from pathlib import Path
from typing import List

from docx import Document  # 依赖 python-docx

from .models import MatchResult

HEADERS = [
    "旧标准名称", "旧标准编号", "新标准名称", "新标准编号", "入库时间", "持有部门"
]


def render_word(results: List[MatchResult], out_path: Path | str) -> Path:
    """将 OBSOLETE 行输出为 Word 表格"""
    out_path = Path(out_path)
    doc = Document()

    table = doc.add_table(rows=1, cols=len(HEADERS))
    for idx, h in enumerate(HEADERS):
        table.rows[0].cells[idx].text = h

    for m in results:
        if m.status != "OBSOLETE":
            continue
        cells = table.add_row().cells
        cells[0].text = m.company.name or ""
        cells[1].text = m.company.code or ""
        cells[2].text = m.company.name or ""   # 公告无新名称字段时占位
        cells[3].text = m.gb_new_code or ""
        cells[4].text = ""  # 入库时间留空
        cells[5].text = m.company.dept or ""

    doc.save(out_path)
    return out_path
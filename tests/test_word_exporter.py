# ==================== tests/test_word_exporter.py =========
from stdsync.core import word_exporter, models
from pathlib import Path

def test_word_exporter(tmp_path):
    """生成 Word 并检查文件存在"""
    dummy = models.MatchResult(
        company=models.CompanyStandard(code="GB/T 1", name="旧名", impl_date=None, dept="质量部"),
        gb_old_code="GB/T 1",
        gb_new_code="GB/T 2",
        status="OBSOLETE",
    )
    doc_path = tmp_path / "demo.docx"
    word_exporter.render_word([dummy], doc_path)
    assert doc_path.exists() and doc_path.stat().st_size > 0
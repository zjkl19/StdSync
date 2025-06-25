# ==================== stdsync/cli.py =======================
"""
简单命令行接口
"""
import argparse
from pathlib import Path
from datetime import datetime

from stdsync.core import excel_io, comparer, reporter
from stdsync.core import word_exporter


def run_cli() -> None:
    """CLI 入口"""
    ap = argparse.ArgumentParser("StdSync CLI")
    ap.add_argument("company", help="公司清单 xlsx")
    ap.add_argument("gb", help="国家公告 xlsx")
    args = ap.parse_args()

    c_df = excel_io.load_company(Path(args.company))
    g_df = excel_io.load_gb(Path(args.gb))
    results = comparer.compare(c_df, g_df)

    out_dir = Path.cwd() / "输出结果"
    out_dir.mkdir(exist_ok=True)
    out_file = out_dir / f"差异_{datetime.now():%Y%m%d_%H%M%S}.xlsx"
    reporter.render(results, out_file)

    doc_file = out_dir / f"差异详情_{datetime.now():%Y%m%d_%H%M%S}.docx"
    word_exporter.render_word(results, doc_file)
    print(f"已生成 {out_file} 以及 {doc_file}")
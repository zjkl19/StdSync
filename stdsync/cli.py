# ==================== stdsync/cli.py =======================
"""
简单命令行接口
"""
import argparse
from pathlib import Path
from datetime import datetime

from stdsync.core import excel_io, comparer, reporter


def run_cli() -> None:
    """CLI 入口"""
    ap = argparse.ArgumentParser("StdSync CLI")
    ap.add_argument("company", help="公司清单 xlsx")
    ap.add_argument("gb", help="国家公告 xlsx")
    args = ap.parse_args()

    c_df = excel_io.load_company(Path(args.company))
    g_df = excel_io.load_gb(Path(args.gb))
    results = comparer.compare(c_df, g_df)

    out_file = Path.cwd() / f"diff_{datetime.now():%Y%m%d}.xlsx"
    reporter.render(results, out_file)

    print(f"已生成 {out_file}")
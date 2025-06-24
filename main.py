# StdSync – 国家与企业标准同步工具
# 入口脚本
# -----------------------------------------------------------
# 用法：
#   python main.py                       # 启动 GUI
#   python main.py --cli "公司清单.xlsx" "国家公告.xlsx"
# -----------------------------------------------------------

import sys
from pathlib import Path

# -----------------------------------------------------------
# 判断是否 CLI 模式
# -----------------------------------------------------------
if len(sys.argv) > 1 and sys.argv[1] == "--cli":
    # 把 "--cli" 从参数中移除，再交给 argparse 解析
    sys.argv.pop(1)

    # CLI 入口
    from stdsync.cli import run_cli

    run_cli()
else:
    # GUI 入口（Tkinter 版）
    from stdsync.gui.tk_app import run_gui

    run_gui()

"""
Tkinter 版 GUI（不依赖任何外部库）
"""
from pathlib import Path
from datetime import datetime
import json
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from stdsync.core import excel_io, comparer, reporter

HISTORY_FILE = Path.home() / ".stdsync_history.json"
MAX_HISTORY = 8


def _load_history() -> list[dict]:
    if HISTORY_FILE.exists():
        try:
            return json.loads(HISTORY_FILE.read_text("utf-8"))
        except Exception:
            return []
    return []


def _save_history(hist: list[dict]):
    HISTORY_FILE.write_text(json.dumps(hist, ensure_ascii=False, indent=2), "utf-8")


# ----------------------------- GUI -----------------------------
class StdSyncGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("StdSync – 国家/企业标准对照")

        self.hist = _load_history()
        self._build_widgets()

    # --- 布局
    def _build_widgets(self):
        frm = ttk.Frame(self, padding=10)
        frm.grid(row=0, column=0, sticky="nsew")

        # 历史记录
        ttk.Label(frm, text="历史记录").grid(row=0, column=0, sticky="w")
        self.cbo_hist = ttk.Combobox(
            frm, values=[h["out"] for h in self.hist], width=60
        )
        self.cbo_hist.grid(row=0, column=1, columnspan=3, sticky="ew", pady=3)

        # 公司清单
        ttk.Label(frm, text="公司清单").grid(row=1, column=0, sticky="w")
        self.ent_company = ttk.Entry(frm, width=50)
        self.ent_company.grid(row=1, column=1, sticky="ew", pady=3)
        ttk.Button(frm, text="浏览", command=self._browse_company).grid(
            row=1, column=2, sticky="ew"
        )

        # 国家公告
        ttk.Label(frm, text="国家公告").grid(row=2, column=0, sticky="w")
        self.ent_gb = ttk.Entry(frm, width=50)
        self.ent_gb.grid(row=2, column=1, sticky="ew", pady=3)
        ttk.Button(frm, text="浏览", command=self._browse_gb).grid(
            row=2, column=2, sticky="ew"
        )

        # 运行按钮
        self.btn_run = ttk.Button(frm, text="运行", command=self._run, state="disabled")
        self.btn_run.grid(row=3, column=0, pady=5)

        # 进度条
        self.pb = ttk.Progressbar(frm, length=300, maximum=100)
        self.pb.grid(row=3, column=1, columnspan=2, pady=5, sticky="ew")

        # 日志框
        self.txt_log = tk.Text(frm, height=12, width=80, state="disabled")
        self.txt_log.grid(row=4, column=0, columnspan=3, pady=5)

        # 状态栏
        self.lbl_status = ttk.Label(frm, text="", foreground="green")
        self.lbl_status.grid(row=5, column=0, columnspan=3, sticky="w")

        # 监听输入框变化
        self.ent_company.bind("<KeyRelease>", self._toggle_run)
        self.ent_gb.bind("<KeyRelease>", self._toggle_run)

    # --- 事件
    def _browse_company(self):
        path = filedialog.askopenfilename(filetypes=[("Excel", "*.xlsx")])
        if path:
            self.ent_company.delete(0, tk.END)
            self.ent_company.insert(0, path)
            self._toggle_run()

    def _browse_gb(self):
        path = filedialog.askopenfilename(filetypes=[("Excel", "*.xlsx")])
        if path:
            self.ent_gb.delete(0, tk.END)
            self.ent_gb.insert(0, path)
            self._toggle_run()

    def _toggle_run(self, *_):
        ready = Path(self.ent_company.get()).is_file() and Path(self.ent_gb.get()).is_file()
        self.btn_run["state"] = "normal" if ready else "disabled"

    def _log(self, msg: str):
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.txt_log["state"] = "normal"
        self.txt_log.insert(tk.END, f"[{ts}] {msg}\n")
        self.txt_log.see(tk.END)
        self.txt_log["state"] = "disabled"

    def _run(self):
        # 后台线程，避免 GUI 卡死
        threading.Thread(target=self._run_core, daemon=True).start()

    def _run_core(self):
        try:
            self.pb["value"] = 10
            self._log("读取文件 …")
            c_df = excel_io.load_company(self.ent_company.get())
            g_df = excel_io.load_gb(self.ent_gb.get())

            self.pb["value"] = 40
            self._log("正在比对 …")
            res = comparer.compare(c_df, g_df)

            self.pb["value"] = 70
            out_path = (
                Path(self.ent_company.get()).parent
                / f"diff_{datetime.now():%Y%m%d}.xlsx"
            )
            reporter.render(res, out_path)

            self.pb["value"] = 100
            obsolete = sum(r.status == "OBSOLETE" for r in res)
            review = sum(r.status == "REVIEW" for r in res)
            status_text = (
                f"{datetime.now():%Y-%m-%d %H:%M:%S} 失效 {obsolete} 条，"
                f"待复核 {review} 条 👉 {out_path.name}"
            )
            self.lbl_status["text"] = status_text
            self.lbl_status["foreground"] = "red" if (obsolete or review) else "green"
            self._log(f"已生成差异表 {out_path}")

            # 写历史
            self.hist.insert(0, {"time": datetime.now().isoformat(), "out": str(out_path)})
            self.hist[:] = self.hist[:MAX_HISTORY]
            _save_history(self.hist)
            self.cbo_hist["values"] = [h["out"] for h in self.hist]

        except Exception as e:
            messagebox.showerror("错误", str(e))
            self._log(f"ERROR: {e}")
        finally:
            self.pb["value"] = 0


# ----------------------------- 入口函数 -----------------------------
def run_gui():
    """给 main.py 调用的入口"""
    app = StdSyncGUI()
    app.mainloop()

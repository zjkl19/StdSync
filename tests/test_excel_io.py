"""
excel_io 模块单元测试
"""
from stdsync.core import excel_io
import pandas as pd


def test_clean_company():
    """确保 clean_company 过滤装饰行并保留有效数据"""
    raw = pd.DataFrame(
        {
            "标准编号": ["部门在用标准清单（9个部门）", "", "Q/FCIC 123—2024"],
            "标准名称": ["", "合计", "测试标准"],
            "代替/修订情况": [None, None, None],
            "实施日期": [None, None, "2025-01-01"],
        }
    )
    cleaned = excel_io.clean_company(raw)
    # 仅剩一条有效记录
    assert len(cleaned) == 1
    # 标准编号应以 Q/FCIC 开头
    assert cleaned.iloc[0]["code"].startswith("Q/FCIC")

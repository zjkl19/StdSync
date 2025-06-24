"""
comparer 模块单元测试
"""
from stdsync.core import comparer
import pandas as pd


def test_compare_obsolete():
    """公司标准被公告明确替代，应标记为 OBSOLETE"""
    company_df = pd.DataFrame(
        {
            "code": ["GB/T 1346—2011"],
            "name": ["水泥测试方法"],
        }
    )
    gb_df = pd.DataFrame(
        {
            "code": ["GB/T 1346—2024"],
            "name": ["水泥测试方法"],
            "replaced": ["GB/T 1346—2011"],
        }
    )

    results = comparer.compare(company_df, gb_df)
    assert results[0].status == "OBSOLETE"

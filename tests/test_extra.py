"""
附加单元测试：
1. 名称相似度 80–89 分 → REVIEW
2. 破折号标准化 → OBSOLETE
3. 自动定位表头（装饰行在最前）
"""
import pandas as pd
from stdsync.core import comparer, excel_io


# ------------------------------------------------------------------
# 1) 名称相似度测试：应判定为 REVIEW
# ------------------------------------------------------------------
def test_compare_review():
    """编号 ≥85% 且名称 ≥85% → REVIEW"""
    company_df = pd.DataFrame(
        {"code": ["GB/T 1346—2008"], "name": ["水泥测试方法"]}
    )
    gb_df = pd.DataFrame(
        {
            "code": ["GB/T 1346—2024"],
            "name": ["水泥测试方法1"],         # 名称相似 ~86
            "replaced": ["GB/T 1346—2002"],  # 编号相似 ~95
        }
    )
    res = comparer.compare(company_df, gb_df)
    assert res[0].status == "REVIEW"
# ------------------------------------------------------------------
# 2) 破折号统一测试：- → — 仍应匹配 OBSOLETE
# ------------------------------------------------------------------
def test_compare_code_normalize():
    company_df = pd.DataFrame(
        {"code": ["GB/T 1346-2011"], "name": ["水泥测试方法"]}  # 半角连字符
    )
    gb_df = pd.DataFrame(
        {
            "code": ["GB/T 1346—2024"],                    # 长破折号
            "name": ["水泥测试方法"],
            "replaced": ["GB/T 1346—2011"],
        }
    )
    res = comparer.compare(company_df, gb_df)
    assert res[0].status == "OBSOLETE"


# ------------------------------------------------------------------
# 3) 自动定位表头：首行装饰 + 表头 + 数据
# ------------------------------------------------------------------
def test_excel_io_find_header(tmp_path):
    """
    构造三行：
      0 行：装饰文字
      1 行：真正表头
      2 行：数据
    load_company() 应返回 1 行数据且包含 'code' 列
    """
    xls_path = tmp_path / "fake_company.xlsx"
    # 用 header=None 写入三行
    pd.DataFrame(
        {
            0: ["部门在用标准清单（9个部门）", "标准编号", "Q/FCIC 123—2024"],
            1: ["", "标准名称", "测试标准"],
            2: ["", "代替/修订情况", ""],
            3: ["", "实施日期", "2025-01-01"],
        }
    ).to_excel(xls_path, header=False, index=False)

    df_clean = excel_io.load_company(xls_path)
    assert len(df_clean) == 1
    assert "code" in df_clean.columns

def test_compare_new_standard_ok():
    """公告行无代替旧号，即便名称相似也应返回 OK"""
    company_df = pd.DataFrame({"code": ["Q/FCIC 001—2024"], "name": ["水泥测试方法"]})
    gb_df = pd.DataFrame({
        "code": ["GB/T 9999—2024"],
        "name": ["水泥测试方法"],   # 相似度 100
        # 'replaced' 缺省 / None
    })
    res = comparer.compare(company_df, gb_df)
    assert res[0].status == "OK"
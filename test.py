import pandas as pd
from pathlib import Path

file = Path(r"公司清单.xlsx")

# 1) 不指定 header，原样读入前 5 行，看看真实数据排布
df = pd.read_excel(file, header=None, nrows=5)
print("---- 前 5 行快照 ----")
print(df)

# 2) 自动查找包含“标准编号”的那一行
for idx, row in df.iterrows():
    if row.astype(str).str.contains("标准编号").any():
        print(f"\n发现真正表头位于第 {idx} 行（从 0 开始计）")
        break

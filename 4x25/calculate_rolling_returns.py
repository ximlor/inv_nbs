import pandas as pd
import numpy as np

# 读取CSV文件
df = pd.read_csv('/Users/ximlor/Documents/Coding/inv_nbs/4x25/data/us_asset_returns.csv')

# 检查数据结构和基本信息
print("数据基本信息:")
print(df.info())
print("\n前5行数据:")
print(df.head())

# 处理百分比数据 - 将百分比字符串转换为小数
# 遍历所有列，除了Year列
for col in df.columns:
    if col != 'Year':
        # 移除百分号并转换为浮点数，然后除以100
        df[col] = df[col].str.rstrip('%').astype(float) / 100

# 确保Year列是整数
df['Year'] = df['Year'].astype(int)

# 按年份排序，确保时间序列正确
df = df.sort_values('Year').reset_index(drop=True)

print("\n处理后的数据基本信息:")
print(df.info())
print("\n处理后的前5行数据:")
print(df.head())

# 计算十年滚动收益率
# 十年滚动收益率 = (1 + r1) * (1 + r2) * ... * (1 + r10) - 1
# 其中r1到r10是连续10年的收益率

# 创建一个函数来计算滚动收益率
def calculate_rolling_return(returns, window=10):
    """
    计算滚动收益率
    returns: 收益率序列
    window: 滚动窗口大小（年数）
    """
    # 使用累积乘积计算滚动收益率
    # 对于每个位置，计算前window年的累积收益率
    rolling_returns = []
    
    for i in range(len(returns)):
        if i < window - 1:
            # 前window-1年数据不足，设为NaN
            rolling_returns.append(np.nan)
        else:
            # 计算过去window年的累积收益率
            period_returns = returns[i-window+1:i+1]
            # 处理可能的缺失值
            if any(pd.isna(period_returns)):
                rolling_returns.append(np.nan)
            else:
                # 累积收益率计算: (1+r1)*(1+r2)*...*(1+rn) - 1
                cumulative_return = np.prod(1 + period_returns) - 1
                rolling_returns.append(cumulative_return)
    
    return rolling_returns

# 为每个资产列计算十年滚动收益率
asset_columns = ['S&P 500 (includes dividends)', '3-month T.Bill', 'US T. Bond (10-year)', 'Gold*', '年平均收益率（名义）']

for asset in asset_columns:
    rolling_col_name = f'{asset}_十年滚动收益率'
    df[rolling_col_name] = calculate_rolling_return(df[asset].values, window=10)

# 显示结果
print("\n包含十年滚动收益率的数据:")
print(df[['Year'] + [col for col in df.columns if '十年滚动收益率' in col]].head(15))

# 保存结果到新的CSV文件
output_file = '/Users/ximlor/Documents/Coding/inv_nbs/4x25/data/us_asset_returns_with_rolling.csv'
df.to_csv(output_file, index=False)

print(f"\n结果已保存到: {output_file}")

# 显示一些统计信息
print("\n十年滚动收益率统计信息:")
rolling_cols = [col for col in df.columns if '十年滚动收益率' in col]
for col in rolling_cols:
    valid_data = df[col].dropna()
    if len(valid_data) > 0:
        print(f"\n{col}:")
        print(f"  数据点数: {len(valid_data)}")
        print(f"  平均值: {valid_data.mean():.4f} ({valid_data.mean()*100:.2f}%)")
        print(f"  标准差: {valid_data.std():.4f}")
        print(f"  最小值: {valid_data.min():.4f} ({valid_data.min()*100:.2f}%)")
        print(f"  最大值: {valid_data.max():.4f} ({valid_data.max()*100:.2f}%)")
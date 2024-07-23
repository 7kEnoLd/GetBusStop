import pandas as pd

# 读取Excel数据
file_path = '数据\天津公交站点-剔除未有路线.xlsx'
df = pd.read_excel(file_path)

# 按照线路分组，汇总每条线路的站点名为集合
route_stations = df.groupby('路线')['名称'].apply(set)

# 获取所有线路名称的集合
route_names = set(route_stations.index)

# 输出结果
print(route_names)

# 如果需要将结果保存到新的DataFrame中
result_df = pd.DataFrame(route_names, columns=['线路名'])

# 如果需要将结果保存为新的Excel文件
output_file_path = '线路名集合.xlsx'
result_df.to_excel(output_file_path, index=False)
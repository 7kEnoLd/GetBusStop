import pandas as pd

# 读取Excel数据
file_path = '数据\天津公交站点-剔除未有路线.xlsx'
df = pd.read_excel(file_path)

# 按照线路分组，汇总每条线路的站点名为集合
route_stations = df.groupby('路线')['名称'].apply(set)

# 创建一个字典用于存储站点集合和对应的线路
station_routes_dict = {}

# 遍历每条线路和站点集合
for route, stations in route_stations.items():
    stations = frozenset(stations)  # 使用frozenset使其可哈希
    if stations not in station_routes_dict:
        station_routes_dict[stations] = []
    station_routes_dict[stations].append(route)

# 找到那些包含相同站点集合的不同线路
duplicate_routes = {stations: routes for stations, routes in station_routes_dict.items() if len(routes) > 1}

# 打印结果
for stations, routes in duplicate_routes.items():
    print(f"相同站点集合: {stations} 存在于线路: {routes}")

# 如果需要将结果保存到新的DataFrame中
result_data = []
for stations, routes in duplicate_routes.items():
    for route in routes:
        result_data.append({'线路名': route, '站点集合': ','.join(stations)})

result_df = pd.DataFrame(result_data)
print(result_df)

# 如果需要将结果保存为新的Excel文件
output_file_path = '筛选结果.xlsx'
result_df.to_excel(output_file_path, index=False)

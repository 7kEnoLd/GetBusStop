import requests
import json
import re
import time
import csv
import os
import pypinyin
from bs4 import BeautifulSoup
import pandas as pd


def get_location(city, linename, mykey):
    print("请耐心等待")
    url_api = 'https://restapi.amap.com/v3/bus/linename?city={}&keywords={}&key={}&extensions=all'.format(city,
                                                                                                          linename,
                                                                                                          mykey)
    res = requests.get(url_api).text  #用requests库发送HTTP请求获取文本形式的API的响应数据
    rt = json.loads(res)  #将返回的json字符串转换为字典

    keyword_parts = linename.split('/')  # 筛选同名线路，如832路/通勤832
    idx = process_buslines(keyword_parts, linename, rt)

    stop = rt['buslines'][idx]['busstops']  # stop 是一个包含车站信息的字典列表，每部字典表示一个车站的信息。

    return [[stop[i]['id'], stop[i]['name'], linename, stop[i]['sequence'], stop[i]['location']] for i in
            range(len(stop))]


def process_buslines(keyword_parts, linename, rt):
    def match_criteria(name, criteria):
        base, temp = criteria
        if '路' not in base:  # 选中第一个分割部分
            base += '路'

        # 查找 base 在 name 中的第一个匹配，如8路
        index = name.find(base)
        if index != -1:
            # 检查 base 前面是否有字符且该字符是否为汉字
            if index > 0 and re.match(r'[\u4e00-\u9fff]', name[index - 1]):
                return False

        if temp == 1:
            return base + '(' in name and '临时' in name
        elif temp == 2:
            return base + '(' in name
        else:
            return base in name

    if rt['status'] != '1':
        print(f"查询失败: {rt['info']}")
        return None

    buslines = rt.get('buslines', [])
    if not buslines:
        print(f"没有找到名称中包含 '{linename}' 的公交线路。")
        return None

    split_keywords = [part.split('(临时)') if '(临时)' in part else [part, ''] for part in keyword_parts]
    found = False

    # 优先查找同时包含 base( 和 临时 的结果
    for index, line in enumerate(buslines):
        name = line['name']
        if any(match_criteria(name, [base, 1]) for base, _ in split_keywords):
            return index

    # 如果没有找到同时包含 base( 和 临时 的结果，再查找仅包含 base( 的结果
    if not found:
        for index, line in enumerate(buslines):
            name = line['name']
            if any(match_criteria(name, [base, 2]) for base, _ in split_keywords):
                return index

    # 如果都没有找到，再查找仅包含 base 的结果，如831路定点，后面没有跟(
    if not found:
        for index, line in enumerate(buslines):
            name = line['name']
            if any(match_criteria(name, [base, 3]) for base, _ in split_keywords):
                return index

    print(f"没有找到名称中包含 '{linename}' 的公交线路。")
    return None


def process_txt_file(file_path):
    with open(file_path, encoding='gbk') as f:
        pattern = r"'(.*?)'"
        data = set()
        for line in f:
            matches = re.findall(pattern, line)
            data.update(matches)
    return data


def load_existing_routes(csv_file):
    if not os.path.exists(csv_file):
        return set()

    df_existing = pd.read_csv(csv_file, encoding='utf-8-sig')
    return set(df_existing['线路编号'].unique())


def write_to_csv(csv_file, rows, mode='a', include_header=False):
    with open(csv_file, mode, encoding='utf-8-sig', newline='') as f:
        csv_writer = csv.writer(f)
        if include_header:
            csv_writer.writerow(["站点ID", "站点名称", "线路编号", "序号", "经纬度"])
        csv_writer.writerows(rows)


def main_conduct(city, mykey, txt_file_path, csv_file_path, processed_lines):
    # 读取和处理txt文件中的数据
    data = process_txt_file(txt_file_path)

    # 加载已存在的CSV文件中的路线，避免重复写入
    existing_routes = load_existing_routes(csv_file_path)

    first_write = not os.path.exists(csv_file_path)
    rows_to_write = []
    new_lines_processed = []

    # 通过容量限制来打断运行
    i = 0

    for linename in data:
        if linename in existing_routes or linename in processed_lines:
            continue

        time.sleep(1)  # 接口并发量限制是1s/次，防止频繁调用 API 导致 API 服务被封禁
        try:
            location_data = get_location(city, linename, mykey)
            if location_data:
                # 转置操作
                # transposed_data = list(zip(*location_data))
                rows_to_write.extend(location_data)
                new_lines_processed.append(linename)
        except Exception as e:
            print(f"获取 {linename} 的数据时出错: {e}")

        i = i + 1
        if i == 5:  # 设置单次限制查询为5
            break

    if rows_to_write:
        write_to_csv(csv_file_path, rows_to_write, mode='a', include_header=first_write)
    else:
        print("没有新的数据需要写入。")

    print(f'已完成当前批次处理。')
    return new_lines_processed


def main(city):
    filename = get_lines(city)
    # '9e4e6c67c9df144256d11235d36d210b'
    mykey = '990981ab890b67b956077f7c081ea433'  # 容量限制，暂时只有一个Key

    processed_lines = []
    while True:
        new_lines_processed = main_conduct(city, mykey, filename, f'{city}公交站点.csv', processed_lines)
        if not new_lines_processed:
            break
        processed_lines.extend(new_lines_processed)

        # 由容量限制执行跳出命令
        if len(new_lines_processed) == 5:
            break

    print(f'所有线路处理完成，输出结果保存在：{city}公交站点.csv')


def get_lines(city):
    if os.path.exists(f"data_{city}.txt"):
        print("已存在路线名称文件，直接使用")
        return f"data_{city}.txt"
    else:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36 Edg/94.0.992.50'}
        print("爬取中")  # 模拟浏览器发送请求
        pinyin_list = pypinyin.pinyin(city, style=pypinyin.NORMAL)  # 设置pypinyin的拼音风格为带声调的拼音
        pinyin_city = ''.join([item[0] for item in pinyin_list])  # 将拼音列表中的每个拼音取出第一个字母，并通过 ''.join() 方法将它们连接成一个字符串
        all_url = f'https://{pinyin_city}.8684.cn/'
        start_html = requests.get(all_url,
                                  headers=headers)  # 使用 BeautifulSoup 库将获取到的 HTML 文本进行解析，生成对象 Soup，以便后续对 HTML 结构进行操作。
        Soup = BeautifulSoup(start_html.text, 'html.parser')
        all_a = Soup.find('div', class_="bus-layer depth w120").find_all(
            'a')  # <div class="bus-layer depth w120">，然后找到其中的所有 <a> 标签，将它们存储在 all_a 变量中
        # 查找所有a标签并过滤href属性包含"line"的标签
        line_links = [a['href'] for a in Soup.find_all('a', href=True) if 'line' in a['href']]
        filename = f"data_{city}.txt"
        Network_list = []
        html = all_url + line_links[0]  # 将目标网站的 URL 地址和 href 属性的值拼接起来，构造出一个新的 URL 地址
        second_html = requests.get(html, headers=headers)
        Soup2 = BeautifulSoup(second_html.text, 'html.parser')
        all_a2 = Soup2.find('div', class_='list clearfix').find_all(
            'a')  # 找到 <div class="list clearfix">，然后找到其中的所有 <a> 标签
        for a2 in all_a2:
            title1 = a2.get_text()
            Network_list.append(title1)
        file = open(filename, 'a')
        file.write(str(Network_list))
        file.close()
        return filename


city = input("输入城市中文名称:")
csv_filename = f'{city}公交站点.csv'
main(city)

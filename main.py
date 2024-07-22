import requests
import json
import re
import time
import csv
import os
import pypinyin
from bs4 import BeautifulSoup

def get_location(city, line, mykey):
    print("请耐心等待")
    url_api = 'https://restapi.amap.com/v3/bus/linename?city={}&keywords={}&key={}&extensions=all'.format(city, line, mykey)
    res = requests.get(url_api).text   #用requests库发送HTTP请求获取文本形式的API的响应数据
    rt = json.loads(res)    #将返回的json字符串转换为字典
    i = 0
    # line_name = rt['buslines'][0]['name']
    # polyline = rt['buslines'][0]['polyline']#经纬度坐标
    # info = [line_name, polyline]   #包含路径名跟坐标点的列表
    stop = rt['buslines'][0]['busstops'] #stop 是一个包含车站信息的字典列表，每个字典表示一个车站的信息。
    # type = rt['buslines'][0]['type']  # 线路类型
    # name = rt['buslines'][0]['name']  # 线路名称
    # start_time = rt['buslines'][0]['start_time']  # 开始营运时间
    # end_time = rt['buslines'][0]['end_time']  # 停止营运时间
    # time_buy = ''
    # try:
    #     time_buy = start_time + '--' + end_time   #计算运行时间
    # except:
    #     pass
    # company = rt['buslines'][0]['company']  # 公交公司
    # distance = rt['buslines'][0]['distance']  # 总里程
    # basic_price = rt['buslines'][0]['basic_price']  # 参考票价
    # form_lines = ""

    # 构造数据结构
    id = []
    name = []
    lineidx = []
    sequence = []
    location = []

    for i in range(len(stop)):
        id.append(stop[i]['id'])
        name.append(stop[i]['name'])
        lineidx.append(line)
        sequence.append(stop[i]['sequence'])
        location.append(stop[i]['location'])


    return [id, name, lineidx, sequence, location]


def main(city):
    # headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36 Edg/94.0.992.50'}
    # print("爬取中")    #模拟浏览器发送请求
    # pinyin_list = pypinyin.pinyin(city, style=pypinyin.NORMAL)  # 设置pypinyin的拼音风格为带声调的拼音
    # pinyin_city = ''.join([item[0] for item in pinyin_list])    #将拼音列表中的每个拼音取出第一个字母，并通过 ''.join() 方法将它们连接成一个字符串
    # all_url = f'https://{pinyin_city}.8684.cn/'
    # start_html = requests.get(all_url, headers=headers)   #使用 BeautifulSoup 库将获取到的 HTML 文本进行解析，生成对象 Soup，以便后续对 HTML 结构进行操作。
    #
    # Soup = BeautifulSoup(start_html.text, 'html.parser')
    # all_a = Soup.find('div', class_="bus-layer depth w120").find_all('a')  # <div class="bus-layer depth w120">，然后找到其中的所有 <a> 标签，将它们存储在 all_a 变量中
    # # 过滤出纯数字的结果
    # all_a = [a.get_text() for a in all_a if re.match(r'^\d+$', a.get_text())]
    #
    # filename = f"data_{city}.txt"
    #
    # # 所有线路
    # # for a in all_a:
    # #     Network_list = []
    # #     html = all_url + '/line' + a #将目标网站的 URL 地址和 href 属性的值拼接起来，构造出一个新的 URL 地址
    # #     second_html = requests.get(html, headers=headers)
    # #     Soup2 = BeautifulSoup(second_html.text, 'html.parser')
    # #     try:
    # #         all_a2 = Soup2.find('div', class_='list clearfix').find_all('a')    #找到 <div class="list clearfix">，然后找到其中的所有 <a> 标签
    # #     except:
    # #         continue
    # #     for a2 in all_a2:
    # #         title1 = a2.get_text()
    # #         Network_list.append(title1)
    # #
    # #     file = open(filename, 'a')
    # #     file.write(str(Network_list))
    # #     file.close()
    #
    #
    # Network_list = []
    # html = all_url + '/line1' #将目标网站的 URL 地址和 href 属性的值拼接起来，构造出一个新的 URL 地址
    # second_html = requests.get(html, headers=headers)
    # Soup2 = BeautifulSoup(second_html.text, 'html.parser')
    # all_a2 = Soup2.find('div', class_='list clearfix').find_all('a')    #找到 <div class="list clearfix">，然后找到其中的所有 <a> 标签
    # for a2 in all_a2:
    #     title1 = a2.get_text()
    #     Network_list.append(title1)
    #
    # file = open(filename, 'a')
    # file.write(str(Network_list))
    # file.close()

    f = open(f'data_{city}.txt', encoding='gbk')  # 载入的txt文件
    txt = []
    for line in f:  # 它将读取文件中的每一行，并将其存储在变量line中。然后，它使用正则表达式r"'(.*?)'
        word = line          #"来查找每个行中以单引号括起来的子字符串，并将这些子字符串存储在变量matches中。
    pattern = r"'(.*?)'"     #最后，这个代码片段将匹配到的所有子字符串存储在一个名为data的列表中
    matches = re.findall(pattern, word)    #findall() 函数，在字符串 word 中查找与给定模式 pattern 匹配的所有子字符串。findall() 函数会返回一个包含所有匹配结果的列表
    data = list(matches)
    a = 0
    # city_chinese="长沙"
    f = open(f'{city}公交站点.csv', 'a', encoding='utf-8-sig', newline="")
    csv_writer = csv.writer(f)
    # 构建列表头
    csv_writer.writerow(["站点ID", "站点名称", "线路编号", "序号", "经纬度"])
    id = []
    name = []
    lineidx = []
    sequence = []
    location = []

    mykey = '9e4e6c67c9df144256d11235d36d210b'

    for i in data:
        time.sleep(0.5) #暂停 0.5 秒，防止频繁调用 API 导致 API 服务被封禁!!!
        a += 1    #已经处理的结果数量

        #if a == 1:  # 加载数量
        #    break
        try:
            line_data = get_location(city, i, mykey)
            with open(f'{city}公交站点.csv', 'a', newline='') as file:
                csv_writer = csv.writer(file)

                # 使用zip进行转置操作
                for row in zip(*line_data):
                    csv_writer.writerow(row)
        except:
            pass
    print(f'已完成，输出结果保存在：{city}公交站点.csv')
    f.close()

city = input("输入城市中文名称:")
csv_filename = f'{city}公交站点.csv'
if not os.path.exists(csv_filename):
    main(city)
else:
    # 如果文件已经存在
    print(f"{csv_filename} 文件已存在，可直接查询")

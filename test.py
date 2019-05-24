# -*- coding: utf-8 -*-
# Python3.5
import requests  # 导入requests
from bs4 import BeautifulSoup  # 导入bs4中的BeautifulSoup
from time import localtime, strftime
from datetime import datetime
import os
import sys
import csv
import warnings

warnings.filterwarnings('ignore')

def current_time():
    return strftime("%Y-%m-%d %H:%M:%S", localtime())

# 定义保存函数，将运算结果保存为txt文件
def text_save(content, filename, mode='a'):
    # Try to save a list variable in txt file.
    file = open(filename, mode, encoding='utf-8')
    for i in range(len(content)):
        file.write(str(content[i]) + '\n')
    file.close()


print('[INFO]>>> begin time:{}'.format(current_time))

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.221 Safari/537.36 SE 2.X MetaSr 1.0'}
all_url = 'http://changsha.8684.cn'  # 开始的URL地址

start_html = requests.get(all_url, headers=headers, verify=False)
Soup = BeautifulSoup(start_html.text, 'lxml')
all_a = Soup.find('div', class_='bus_kt_r1').find_all('a') + \
        Soup.find('div', class_='bus_kt_r2').find_all('a') 

print('[INFO]>>> All soup:{}'.format(all_a))

Network_list = []
station_list = []
all_station  = []

for a in all_a:
    href = a['href']  # 取出a标签的href 属性
    html = all_url + href
    print('[INFO]>>> processing first url:{}'.format(html))
    second_html = requests.get(html, headers=headers, verify=False)
    #print (second_html.text)
    Soup2 = BeautifulSoup(second_html.text, 'lxml')
    all_a2 = Soup2.find('div', class_='cc_content').find_all(
        'div')[-1].find_all('a')  # 既有id又有class的div不知道为啥取不出来，只好迂回取了
    for a2 in all_a2:
        title1 = a2.get_text()  # 取出a1标签的文本
        href1 = a2['href']  # 取出a标签的href 属性
        #print (title1,href1)
        html_bus = all_url + href1
        print('[INFO]>>> processing bus url:{}'.format(html_bus))
        thrid_html = requests.get(html_bus, headers=headers, verify=False)
        # print('[INFO]>>> encoding:{}'.format(thrid_html.encoding))
        Soup3 = BeautifulSoup(thrid_html.content, 'lxml')
        bus_name = Soup3.find('div', class_='bus_i_t1').find('h1').get_text()
        bus_type = Soup3.find('div', class_='bus_i_t1').find('a').get_text()
        bus_time = Soup3.find_all('p', class_='bus_i_t4')[0].get_text()
        bus_cost = Soup3.find_all('p', class_='bus_i_t4')[1].get_text()
        bus_company = Soup3.find_all('p', class_='bus_i_t4')[
            2].find('a').get_text()
        bus_update = Soup3.find_all('p', class_='bus_i_t4')[3].get_text()
        bus_label = Soup3.find('div', class_='bus_label')
        if bus_label:
            bus_length = bus_label.get_text()
        else:
            bus_length = []
        #print (bus_name,bus_type,bus_time,bus_cost,bus_company,bus_update)
        all_line = Soup3.find_all('div', class_='bus_line_top')
        all_site = Soup3.find_all('div', class_='bus_line_site')
        line_x = all_line[0].find('div', class_='bus_line_txt').get_text()[
            :-9] + all_line[0].find_all('span')[-1].get_text()
        sites_x = all_site[0].find_all('a')
        sites_x_list = []
        for site_x in sites_x:
            sites_x_list.append(site_x.get_text())
        line_num = len(all_line)
        if line_num == 2:  # 如果存在环线，也返回两个list，只是其中一个为空
            line_y = all_line[1].find('div', class_='bus_line_txt').get_text()[
                :-9] + all_line[1].find_all('span')[-1].get_text()
            sites_y = all_site[1].find_all('a')
            sites_y_list = []
            for site_y in sites_y:
                sites_y_list.append(site_y.get_text())
        else:
            line_y, sites_y_list = [], []
        information = [bus_name, bus_type, bus_time, bus_cost, bus_company,
                       bus_update, bus_length, line_x, sites_x_list, line_y, sites_y_list]

        if sites_x_list[0] == sites_x_list[-1] :
                station_list.append(sites_x_list)
        else:
                station_list.append(sites_x_list)
                station_list.append(sites_y_list)

        if sites_x_list != sites_y_list.reverse():
            for rec in set(sites_x_list + sites_y_list):
                all_station.append(rec)
        else:
            for rec in sites_x_list:
                all_station.append(rec)

        Network_list.append(information)
        # if(len(Network_list) == 10):
        #     text_save(Network_list,'Network_bus.txt');
        #     sys.exit()



# 输出处理后的数据     
text_save(Network_list,'Network_bus.txt')

with open('station_line.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer  = csv.writer(csvfile)
    for data in station_list:
        writer.writerow(data)

with open('station_all.csv', 'a', newline='', encoding='utf-8') as csvfile:
    writer  = csv.writer(csvfile)
    writer.writerow(all_station)

print('[INFO]>>> end time:{}'.format(current_time))


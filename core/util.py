#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2023/3/29 10:28
# @Author : chaocai

import json
import os
import requests

from core import config


# 加载数据，批量加载合并排序
def file_load():
    result_list = []
    input_path = config.read_config('input_path')
    for file_name in os.listdir(input_path):
        if file_name != 'pc.txt':
            file_path = input_path + file_name
            with open(file_path, encoding='utf-8') as f:
                read = f.read()
                try:
                    data_list = json.loads(read)['data']['data'][0]['rows']
                    result_list.extend(data_list)
                except:
                    pass
    # 时间排序
    return sorted(result_list, key=lambda x: (x['time']))


# 删除输出文件
def del_file(path):
    if os.path.isfile(path):
        os.remove(path)


# 输出结果
def write_data(result_map):
    print('输出对手数量：%s' % len(result_map))
    with open(config.read_config('output_path'), 'a', encoding='utf-8') as f:
        f.write('PC\n')
    for key in result_map:
        with open(config.read_config('output_path'), 'a', encoding='utf-8') as f:
            f.write(result_map[key])
    with open(config.read_config('output_path'), 'a', encoding='utf-8') as f:
        f.write('ENDPC')


# 通用post请求
def http_post(url, param, fail_info):
    proxy = config.read_config('proxy_url') if config.read_config('proxy_url') else None
    proxies = {'http': proxy}
    headers = config.read_config('headers')
    headers['Cookie'] = config.read_config('cookie')
    text = None
    try:
        response = requests.post(url=url, data=param, headers=headers, proxies=proxies, timeout=10)
        if not response.status_code == 200:
            print(fail_info)
        text = response.text
    except Exception as e:
        print(e)
    return text


# 通用get请求
def http_get(url, param, fail_info):
    proxy = config.read_config('proxy_url') if config.read_config('proxy_url') else None
    proxies = {'http': proxy}
    headers = config.read_config('headers')
    headers['Cookie'] = config.read_config('cookie')
    text = None
    try:
        response = requests.get(url=url, params=param, headers=headers, proxies=proxies, timeout=10)
        if not response.status_code == 200:
            print(fail_info)
        text = response.text
    except Exception as e:
        print(e)
    return text

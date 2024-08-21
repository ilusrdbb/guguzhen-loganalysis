#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2023/3/29 10:28
# @Author : chaocai

import datetime
import json
import os
import time

import requests

from core import config, enemy


# 解析收割机脚本导出文件
def file_load():
    json_data_list = []
    input_path = config.read_config('input_path')
    # 遍历文件夹下的收割机导出文件
    for file_name in os.listdir(input_path):
        if file_name != 'pc.txt':
            file_path = input_path + file_name
            with open(file_path, encoding='utf-8') as f:
                read = f.read()
                try:
                    json_data = json.loads(read)['data']['data'][0]['rows']
                    json_data_list.extend(json_data)
                except:
                    pass
    # 过滤获取需要分析的进攻/防守数据
    filter_enemy_dict = get_filter_dict(json_data_list)
    # 权重统计 论坛获取系数 防守记录分析
    w_dict = get_w_dict(filter_enemy_dict)
    return {
        'enemy_list': sorted(filter_enemy_dict['attack_enemy_list'], key=lambda x: x.battle_timestamp),
        'w_dict': w_dict
    }


# 获取权重和论坛系数
def get_w_dict(filter_enemy_dict):
    result_map = {}
    # 进攻记录
    for attack_enemy in filter_enemy_dict['attack_enemy_list']:
        # 计数
        if attack_enemy.enemy_name in result_map:
            result_map[attack_enemy.enemy_name]['weight'] += 1
        else:
            result_map[attack_enemy.enemy_name] = {'enemy_name': attack_enemy.enemy_name,
                                                   'enemy_card': attack_enemy.enemy_card,
                                                   'kf_level': attack_enemy.kf_level,
                                                   'weight': 1}
            if config.read_config('is_search_level') and config.read_config('cookie') \
                    and attack_enemy.card_level >= 850:
                # 通过论坛发帖获取真实的系数
                kf_level = enemy.get_kf_level(attack_enemy.enemy_name)
                if kf_level:
                    result_map[attack_enemy.enemy_name]['kf_level'] = kf_level
    return result_map


# 过滤获取需要分析的进攻/防守数据
def get_filter_dict(json_data):
    attack_enemy_list = []
    defense_enemy_list = []
    for data in json_data:
        # 排除野怪结果
        if data['char'] == '野怪':
            continue
        # 段位限制
        if config.read_config('rank_limit') and data.get('rank') \
                and data.get('rank') != config.read_config('rank_limit'):
            continue
        # 初始化对手数据
        enemy_data = enemy.Enemy(data)
        # 白名单
        if config.read_config('white_list') and enemy_data.enemy_name not in config.read_config('white_list'):
            continue
        # 黑名单跳过
        if config.read_config('black_list') and enemy_data.enemy_name in config.read_config('black_list'):
            continue
        # 等级跳过
        if config.read_config('min_card_level') and enemy_data.card_level < config.read_config('min_card_level'):
            continue
        # 日期范围跳过
        if config.read_config('start_date'):
            start_datetime = datetime.datetime.strptime(config.read_config('start_date') + ' 00:00:00.000',
                                                        "%Y-%m-%d %H:%M:%S.%f")
            start_timestamp = int(time.mktime(start_datetime.timetuple()) * 1000.0 + start_datetime.microsecond / 1000.0)
            if start_timestamp > enemy_data.battle_timestamp:
                continue
        if config.read_config('end_date'):
            end_datetime = datetime.datetime.strptime(config.read_config('end_date') + ' 23:59:59.999',
                                                      "%Y-%m-%d %H:%M:%S.%f")
            end_timestamp = int(time.mktime(end_datetime.timetuple()) * 1000.0 + end_datetime.microsecond / 1000.0)
            if end_timestamp < enemy_data.battle_timestamp:
                continue
        # 进攻/防守
        if data.get('type') == 'defense':
            defense_enemy_list.append(enemy_data)
        else:
            attack_enemy_list.append(enemy_data)
    return {
        'attack_enemy_list': attack_enemy_list,
        'defense_enemy_list': defense_enemy_list
    }


# 删除输出文件
def del_file(path):
    if os.path.isfile(path):
        os.remove(path)


# 输出结果至文本文件
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
    time.sleep(1)
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
    time.sleep(1)
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


# 将字典中元素移动至末尾
def move_element_to_end(input_dict, key_to_move):
    if key_to_move in input_dict:
        # 弹出元素并保存其值
        element_value = input_dict.pop(key_to_move)
        # 重新将元素添加到字典的末尾
        input_dict[key_to_move] = element_value

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2023/3/29 10:28
# @Author : chaocai

import json
import os
import time
import datetime
import random

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
    defense_cache = {}
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
                    and attack_enemy.card_level == 850:
                # 通过论坛发帖获取真实的系数
                kf_level = enemy.get_kf_level(attack_enemy.enemy_name)
                if kf_level:
                    result_map[attack_enemy.enemy_name]['kf_level'] = kf_level
    # 防守记录
    if config.read_config('is_analyse_defense'):
        for defense_enemy in filter_enemy_dict['defense_enemy_list']:
            if defense_enemy.enemy_name in result_map:
                defense_level = result_map[defense_enemy.enemy_name]['kf_level']
            elif defense_enemy.enemy_name in defense_cache:
                defense_level = defense_cache[defense_enemy.enemy_name]
            elif config.read_config('is_search_level') and config.read_config('cookie') \
                    and defense_enemy.card_level == 850:
                defense_level = enemy.get_kf_level(defense_enemy.enemy_name)
            else:
                defense_level = defense_enemy.kf_level
            if defense_level:
                # 防守获取的等级写入缓存，防止重复网络请求
                defense_cache[defense_enemy.enemy_name] = defense_level
                # 获取匹配数据
                match_name = match_defense_name(defense_enemy.enemy_name, defense_enemy.enemy_card,
                                                defense_level, result_map)
                if match_name:
                    result_map[match_name]['weight'] += 1
    return result_map


# 防守数据匹配进攻数据
def match_defense_name(defense_name, defense_card, defense_level, result_map):
    # 名称与卡片匹配
    if result_map.get(defense_name) and result_map.get(defense_name).get('enemy_card'):
        return defense_name
    # 不匹配卡片时匹配进攻记录最接近系数的同卡片记录
    match_list = []
    for enemy_name in result_map:
        if result_map[enemy_name].get('kf_level') and result_map[enemy_name]['enemy_card'] == defense_card:
            match_list.append(result_map[enemy_name])
    if match_list:
        # 找最接近系数的
        return random.choice(find_closest_dicts(defense_level, match_list))['enemy_name']
    return None


# 找最接近系数的list
def find_closest_dicts(target_num, dict_list):
    if not target_num:
        target_num = config.read_config('max_kf_level')
    closest_dicts = []
    # 初始化最小差值
    min_difference = 2000
    for dictionary in dict_list:
        num = dictionary.get("kf_level")
        # 计算差值的绝对值
        difference = abs(target_num - num)
        if difference < min_difference:
            # 重置最接近的字典列表
            closest_dicts = [dictionary]
            # 更新最小差值
            min_difference = difference
        elif difference == min_difference:
            # 如果有多个字典与最小差值相等，则添加到列表中
            closest_dicts.append(dictionary)
    return closest_dicts


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

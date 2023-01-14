#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2023/1/4 9:50
# @Author : chaocai

from config import *


# 获取装备list
def get_gear_list(battle_log_dom):
    result_list = []
    try:
        result_list.append(GEAR_MAP[battle_log_dom.xpath(XPATH_CONFIG['GEAR'])[4]])
        result_list.append(GEAR_MAP[battle_log_dom.xpath(XPATH_CONFIG['GEAR'])[5]])
        result_list.append(GEAR_MAP[battle_log_dom.xpath(XPATH_CONFIG['GEAR'])[6]])
        result_list.append(GEAR_MAP[battle_log_dom.xpath(XPATH_CONFIG['GEAR'])[7]])
    except:
        pass
    return result_list


# 获取对应属性总和
def get_sum_point(gear_list, type):
    result = 0
    for gear in gear_list:
        attribute_map = DEFAULT_GEAR[gear]
        try:
            result = result + attribute_map[type]
        except:
            continue
    return result



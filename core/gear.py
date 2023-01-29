#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2023/1/4 9:50
# @Author : chaocai
import copy
import re

from config import *


# 获取装备list
def get_gear_list(battle_log_dom):
    return [GEAR_MAP[battle_log_dom.xpath(XPATH_CONFIG['GEAR'])[4]],
                   GEAR_MAP[battle_log_dom.xpath(XPATH_CONFIG['GEAR'])[5]],
                   GEAR_MAP[battle_log_dom.xpath(XPATH_CONFIG['GEAR'])[6]],
                   GEAR_MAP[battle_log_dom.xpath(XPATH_CONFIG['GEAR'])[7]]]


# 获取装备等级list
def get_level_list(battle_log_dom):
    return [battle_log_dom.xpath(XPATH_CONFIG['LEVEL'])[4],
                   battle_log_dom.xpath(XPATH_CONFIG['LEVEL'])[5],
                   battle_log_dom.xpath(XPATH_CONFIG['LEVEL'])[6],
                   battle_log_dom.xpath(XPATH_CONFIG['LEVEL'])[7]]


# 获取红色装备list
def get_red_list(battle_log_dom, gear_list):
    result_list = []
    try:
        color_list = [int(re.findall(MATCH_CONFIG['COLOR'], battle_log_dom.xpath(XPATH_CONFIG['COLOR'])[4])[0]),
                      int(re.findall(MATCH_CONFIG['COLOR'], battle_log_dom.xpath(XPATH_CONFIG['COLOR'])[5])[0]),
                      int(re.findall(MATCH_CONFIG['COLOR'], battle_log_dom.xpath(XPATH_CONFIG['COLOR'])[6])[0]),
                      int(re.findall(MATCH_CONFIG['COLOR'], battle_log_dom.xpath(XPATH_CONFIG['COLOR'])[7])[0])]
    except:
        # 未安装装主题包的情况下会报错，再尝试读取
        try:
            color_list = [int(re.findall(MATCH_CONFIG['COLOR2'], battle_log_dom.xpath(XPATH_CONFIG['COLOR'])[4])[0]),
                          int(re.findall(MATCH_CONFIG['COLOR2'], battle_log_dom.xpath(XPATH_CONFIG['COLOR'])[5])[0]),
                          int(re.findall(MATCH_CONFIG['COLOR2'], battle_log_dom.xpath(XPATH_CONFIG['COLOR'])[6])[0]),
                          int(re.findall(MATCH_CONFIG['COLOR2'], battle_log_dom.xpath(XPATH_CONFIG['COLOR'])[7])[0])]
        except:
            # 最原始的咕咕镇自带路径
            try:
                color_list = [5 if re.findall(MATCH_CONFIG['COLOR3'], battle_log_dom.xpath(XPATH_CONFIG['COLOR'])[4])[0] == '#EA644A' else 0,
                    5 if re.findall(MATCH_CONFIG['COLOR3'], battle_log_dom.xpath(XPATH_CONFIG['COLOR'])[5])[0] == '#EA644A' else 0,
                    5 if re.findall(MATCH_CONFIG['COLOR3'], battle_log_dom.xpath(XPATH_CONFIG['COLOR'])[6])[0] == '#EA644A' else 0,
                    5 if re.findall(MATCH_CONFIG['COLOR3'], battle_log_dom.xpath(XPATH_CONFIG['COLOR'])[7])[0] == '#EA644A' else 0]
            except:
                # 自定义就无能为力了
                color_list = []
    if gear_list and color_list and len(gear_list) == len(color_list):
        for i in range(0, len(gear_list)):
            gear = gear_list[i]
            color = color_list[i]
            if color == 5:
                result_list.append(gear)
    return result_list


# 获取对应属性总和
def get_sum_point(_gear_list, type):
    result = 0
    if _gear_list and type:
        for gear_map in _gear_list:
            try:
                result = result + gear_map[type]
            except:
                continue
    return result


# 属性百分比转属性
def get_gear_map_list(gear_list, level_list, red_list):
    result_list = []
    if gear_list and level_list and len(gear_list) == len(level_list):
        for i in range(0, len(gear_list)):
            gear = gear_list[i]
            gear_level = int(level_list[i])
            _gear = {}
            gear_percent = copy.deepcopy(DEFAULT_GEAR[gear])
            if gear == 'STAFF':
                _gear = get_staff(gear_percent, gear_level)
            elif gear == 'BLADE':
                _gear = get_blade(gear_percent, gear_level)
            elif gear == 'ASSBOW':
                _gear = get_assbow(gear_percent, gear_level)
            elif gear == 'DAGGER':
                _gear = get_dagger(gear_percent, gear_level)
            elif gear == 'WAND':
                _gear = get_wand(gear_percent, gear_level)
            elif gear == 'SHIELD':
                _gear = get_shield(gear_percent, gear_level)
            elif gear == 'CLAYMORE':
                _gear = get_claymore(gear_percent, gear_level)
            elif gear == 'SPEAR':
                _gear = get_spear(gear_percent, gear_level)
            elif gear == 'GLOVES':
                _gear = get_gloves(gear_percent, gear_level)
            elif gear == 'BRACELET':
                _gear = get_bracelet(gear_percent, gear_level)
            elif gear == 'VULTURE':
                _gear = get_vulture(gear_percent, gear_level)
            elif gear == 'CLOAK':
                _gear = get_cloak(gear_percent, gear_level)
            elif gear == 'THORN':
                _gear = get_thorn(gear_percent, gear_level, gear, red_list)
            elif gear == 'WOOD':
                _gear = get_wood(gear_percent, gear_level)
            elif gear == 'CAPE':
                _gear = get_cape(gear_percent, gear_level)
            elif gear == 'SCARF':
                _gear = get_scarf(gear_percent, gear_level)
            elif gear == 'TIARA':
                _gear = get_tiara(gear_percent, gear_level)
            elif gear == 'RIBBON':
                _gear = get_ribbon(gear_percent, gear_level)
            elif gear == 'RING':
                _gear = get_ring(gear_percent, gear_level)
            elif gear == 'DEVOUR':
                _gear = get_devour(gear_percent, gear_level)
            result_list.append(_gear)
    return result_list


def get_devour(gear_percent, gear_level):
    for key in gear_percent:
        if key == '_MTH':
            gear_percent[key] = int(gear_level * 0.5 * (gear_percent[key] / 100))
        elif key == '_SKL':
            gear_percent[key] = int(gear_level * 0.8 * (gear_percent[key] / 100))
    return gear_percent


def get_ring(gear_percent, gear_level):
    for key in gear_percent:
        if key == '_PTH':
            gear_percent[key] = int(gear_level * 0.5 * (gear_percent[key] / 100))
        elif key == '_MTH':
            gear_percent[key] = int(gear_level * 0.5 * (gear_percent[key] / 100))
        elif key == '_CRT':
            gear_percent[key] = int(gear_level * 0.8 * (gear_percent[key] / 100))
        elif key == '_SKL':
            gear_percent[key] = int(gear_level * 0.8 * (gear_percent[key] / 100))
    return gear_percent


def get_ribbon(gear_percent, gear_level):
    for key in gear_percent:
        if key == '_HPR':
            gear_percent[key] = int(gear_level * 5 * (gear_percent[key] / 100))
        elif key == 'SLDR':
            gear_percent[key] = int(gear_level / 30 * (gear_percent[key] / 100))
    return gear_percent


def get_tiara(gear_percent, gear_level):
    for key in gear_percent:
        if key == '_PDEC':
            gear_percent[key] = int(gear_level * 2 * (gear_percent[key] / 100))
    return gear_percent


def get_scarf(gear_percent, gear_level):
    for key in gear_percent:
        if key == '_PDEC':
            gear_percent[key] = int(gear_level * 2 * (gear_percent[key] / 100))
        elif key == '_MDEC':
            gear_percent[key] = int(gear_level * 2 * (gear_percent[key] / 100))
        elif key == '_HPR':
            gear_percent[key] = int(gear_level * 4 * (gear_percent[key] / 100))
    return gear_percent


def get_cape(gear_percent, gear_level):
    for key in gear_percent:
        if key == '_MDEC':
            gear_percent[key] = int(gear_level * 5 * (gear_percent[key] / 100))
    return gear_percent


def get_wood(gear_percent, gear_level):
    for key in gear_percent:
        if key == '_HPR':
            gear_percent[key] = int(gear_level * 20 * (gear_percent[key] / 100))
        elif key == '_PDEC':
            gear_percent[key] = int(gear_level * 5 * (gear_percent[key] / 100))
        elif key == '_MDEC':
            gear_percent[key] = int(gear_level * 5 * (gear_percent[key] / 100))
    return gear_percent


def get_thorn(gear_percent, gear_level, gear, red_list):
    for key in gear_percent:
        if key == 'RFL':
            gear_percent[key] = int((gear_level / 15 + 10) * (gear_percent[key] / 100))
            # 神秘
            if gear in DEFULT_SECRET:
                gear_percent[key] = gear_percent[key] + THRON_ADD_RFL
            elif gear in red_list and gear in DEFULT_RED_SECRET:
                gear_percent[key] = gear_percent[key] + THRON_ADD_RFL
    return gear_percent


def get_cloak(gear_percent, gear_level):
    for key in gear_percent:
        if key == '_SLDR':
            gear_percent[key] = int(gear_level * 60 * (gear_percent[key] / 100))
    return gear_percent


def get_vulture(gear_percent, gear_level):
    for key in gear_percent:
        if key == 'LCH':
            gear_percent[key] = int((gear_level / 15 + 1) * (gear_percent[key] / 300)) * 3
        elif key == '_SPD':
            gear_percent[key] = int(gear_level * 2 * (gear_percent[key] / 100))
    return gear_percent


def get_bracelet(gear_percent, gear_level):
    for key in gear_percent:
        if key == 'MATK':
            gear_percent[key] = int((gear_level / 5 + 1) * (gear_percent[key] / 100))
        elif key == 'MTH':
            gear_percent[key] = int((gear_level / 20 + 1) * (gear_percent[key] / 100))
    return gear_percent


def get_gloves(gear_percent, gear_level):
    for key in gear_percent:
        if key == '_PATK':
            gear_percent[key] = int(gear_level * 10 * (gear_percent[key] / 100))
        elif key == '_MATK':
            gear_percent[key] = int(gear_level * 10 * (gear_percent[key] / 100))
        elif key == '_SPD':
            gear_percent[key] = int(gear_level * 2 * (gear_percent[key] / 100))
    return gear_percent


def get_spear(gear_percent, gear_level):
    for key in gear_percent:
        if key == 'PATK':
            gear_percent[key] = int((gear_level / 5 + 50) * (gear_percent[key] / 100))
        elif key == 'PTH':
            gear_percent[key] = int((gear_level / 20 + 10) * (gear_percent[key] / 100))
        elif key == '_MTH':
            gear_percent[key] = int(gear_level * 2 * (gear_percent[key] / 100))
        elif key == 'LCH':
            gear_percent[key] = int((gear_level / 15 + 10) * (gear_percent[key] / 100))
    return gear_percent


def get_claymore(gear_percent, gear_level):
    for key in gear_percent:
        if key == '_PATK':
            gear_percent[key] = int(gear_level * 20 * (gear_percent[key] / 200)) * 2
        elif key == 'PATK':
            gear_percent[key] = int((gear_level / 5 + 30) * (gear_percent[key] / 100))
        elif key == 'CTH':
            gear_percent[key] = int((gear_level / 20 + 1) * (gear_percent[key] / 100))
    return gear_percent


def get_shield(gear_percent, gear_level):
    for key in gear_percent:
        if key == 'LCH':
            gear_percent[key] = int((gear_level / 5 + 10) * (gear_percent[key] / 100))
        elif key == 'RFL':
            gear_percent[key] = int(gear_level / 15 * (gear_percent[key] / 100))
            # 反伤樱桃的10反
            if 'RFL' not in DEFAULT_AMULET and IS_SHIELD_ADD_RFL:
                gear_percent[key] = gear_percent[key] + MAX_ADD_RFL
    return gear_percent


def get_wand(gear_percent, gear_level):
    for key in gear_percent:
        if key == 'MATK':
            gear_percent[key] = int(gear_level / 5 * (gear_percent[key] / 300)) * 3
        elif key == 'PTH':
            gear_percent[key] = int(gear_level / 20 * (gear_percent[key] / 100))
    return gear_percent


def get_dagger(gear_percent, gear_level):
    for key in gear_percent:
        if key == 'PATK':
            gear_percent[key] = int(gear_level / 5 * (gear_percent[key] / 100))
        elif key == 'MATK':
            gear_percent[key] = int(gear_level / 5 * (gear_percent[key] / 100))
        elif key == '_SPD':
            gear_percent[key] = int(gear_level * 4 * (gear_percent[key] / 100))
        elif key == 'SPD':
            gear_percent[key] = int((gear_level / 5 + 25) * (gear_percent[key] / 100))
    return gear_percent


def get_assbow(gear_percent, gear_level):
    for key in gear_percent:
        if key == 'PATK':
            gear_percent[key] = int((gear_level / 5 + 30) * (gear_percent[key] / 100))
        elif key == 'PTH':
            gear_percent[key] = int((gear_level / 20 + 10) * (gear_percent[key] / 100))
        elif key == 'CTH':
            gear_percent[key] = int((gear_level / 20 + 10) * (gear_percent[key] / 100))
        elif key == '_PTH':
            gear_percent[key] = int(gear_level * (gear_percent[key] / 100))
    return gear_percent


def get_staff(gear_percent, gear_level):
    for key in gear_percent:
        if key == '_PATK':
            gear_percent[key] = int(gear_level * 10 * (gear_percent[key] / 100))
        elif key == '_MATK':
            gear_percent[key] = int(gear_level * 10 * (gear_percent[key] / 100))
        elif key == 'MTH':
            gear_percent[key] = int((gear_level / 20 + 5) * (gear_percent[key] / 100))
        elif key == 'LCH':
            gear_percent[key] = int((gear_level / 15 + 10) * (gear_percent[key] / 100))
    return gear_percent


def get_blade(gear_percent, gear_level):
    for key in gear_percent:
        if key == 'PATK':
            gear_percent[key] = int((gear_level / 5 + 20) * (gear_percent[key] / 100))
        elif key == 'PTH':
            gear_percent[key] = int((gear_level / 20 + 10) * (gear_percent[key] / 100))
        elif key == 'CTH':
            gear_percent[key] = int((gear_level / 20 + 10) * (gear_percent[key] / 100))
        elif key == 'SPD':
            gear_percent[key] = int((gear_level / 5 + 20) * (gear_percent[key] / 100))
    return gear_percent









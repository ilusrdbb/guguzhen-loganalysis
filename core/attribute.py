#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2023/6/6 10:02
# @Author : chaocai
import re

from core import config


class Attribute:
    # 总点数
    final_point = 0
    # 全部剩余点数
    all_point = 0
    # 力量
    t_str = 0
    # 敏捷
    t_agi = 0
    # 智力
    t_int = 0
    # 体魄
    t_vit = 0
    # 精神
    t_spr = 0
    # 意志
    t_mnd = 0

    # 初始化
    def __init__(self, enemy):
        self.all_point = int((6 + enemy.card_level * 3) * (100 + enemy.card_quality) / 100)
        self.final_point = self.all_point


# 点数计算
def cal_attr(enemy_data, battle_data, attr_data, aumlet_str):
    attr_list = battle_data.attr_list
    attr_data.t_str = attr_list[0]
    attr_data.t_agi = attr_list[1]
    attr_data.t_int = attr_list[2]
    attr_data.t_vit = attr_list[3]
    attr_data.t_spr = attr_list[4]
    attr_data.t_mnd = attr_list[5]
    if attr_data.t_str.isdigit():
        # 旧数据点数 直接返回
        return
    # 根据血量和护盾 推测意志、精神、体魄
    cal_hp_sld(enemy_data, battle_data, attr_data, aumlet_str)
    # 根据剩余点数和图标大致推断力量、智力、敏捷
    cal_other_attr(battle_data, attr_data, enemy_data)


# 根据剩余点数和图标大致推断力量、智力、敏捷
def cal_other_attr(battle_data, attr_data, enemy_data):
    if attr_data.all_point == 0:
        return
    icon_list = battle_data.attr_list
    # 先看速度
    if 'double-angle-up' in icon_list[1]:
        if 'icon-angle-up' in icon_list[0] or 'icon-angle-up' in icon_list[2]:
            # 取3/5的剩余点数
            t_agi = int(attr_data.all_point * 3 / 5)
        elif 'icon-angle-up' in icon_list[0] or 'icon-angle-up' in icon_list[2]:
            # 取3/4的剩余点数
            t_agi = int(attr_data.all_point * 3 / 4)
        else:
            attr_data.t_agi = attr_data.all_point - 2
            attr_data.t_str = 1
            attr_data.t_int = 1
            return
    else:
        t_agi = int(attr_data.final_point * agi_ratio(icon_list[1]))
    if t_agi >= attr_data.all_point - 2:
        attr_data.t_agi = attr_data.all_point - 2
        attr_data.t_str = 1
        attr_data.t_int = 1
        return
    attr_data.t_agi = t_agi
    attr_data.all_point -= t_agi
    # 智力
    t_int = int(attr_data.final_point * int_ratio(icon_list[2]))
    if enemy_data.kf_level >= 1400 and 'double-angle-up' in icon_list[2]:
        if t_int <= 1600:
            t_int = 1600
    if t_int >= attr_data.all_point - 1:
        if enemy_data.kf_level >= 1400 and 'double-angle-up' in icon_list[2]:
            # 先从精神拿 然后是敏捷
            diff = 1600 - attr_data.all_point + 1
            if diff < attr_data.t_spr:
                attr_data.t_spr -= diff
                attr_data.t_int = 1600
                attr_data.t_str = 1
                return
            else:
                diff -= (attr_data.t_spr - 1)
                attr_data.t_spr = 1
                attr_data.t_agi -= diff
                attr_data.t_str = 1
                attr_data.t_int = 1600
                return
        else:
            attr_data.t_int = attr_data.all_point - 1
            attr_data.t_str = 1
            return
    attr_data.t_int = t_int
    attr_data.all_point -= t_int
    # 力量
    attr_data.t_str = attr_data.all_point
    if enemy_data.kf_level >= 1300 and 'double-angle-up' in icon_list[0]:
        if attr_data.t_str <= 1500:
            attr_data.t_str = 1500
            diff = 1500 - attr_data.all_point
            if attr_data.all_point < 1500:
                # 先从意志拿 然后是敏捷
                if diff < attr_data.t_mnd:
                    attr_data.t_mnd -= diff
                else:
                    diff -= (attr_data.t_mnd - 1)
                    attr_data.t_mnd = 1
                    attr_data.t_agi -= diff
    # 补偿
    if 'double-angle-down' in icon_list[0]:
        if 'angle-down' not in icon_list[5]:
            attr_data.t_mnd += (attr_data.all_point - 1)
            attr_data.t_str = 1
        elif 'angle-down' not in icon_list[3]:
            attr_data.t_vit += (attr_data.all_point - 1)
            attr_data.t_str = 1
        elif 'angle-down' not in icon_list[2]:
            attr_data.t_int += (attr_data.all_point - 1)
            attr_data.t_str = 1
        elif 'angle-down' not in icon_list[4]:
            attr_data.t_spr += (attr_data.all_point - 1)
            attr_data.t_str = 1
        else:
            attr_data.t_agi += (attr_data.all_point - 1)
            attr_data.t_str = 1


# 根据血量和护盾计算
def cal_hp_sld(enemy_data, battle_data, attr_data, aumlet_str):
    cal_sld(enemy_data, battle_data, attr_data, aumlet_str)
    cal_hp(enemy_data, battle_data, attr_data, aumlet_str)


# 护盾计算
def cal_sld(enemy_data, battle_data, attr_data, aumlet_str):
    icon_list = battle_data.attr_list
    gear_list = battle_data.gear_list
    gear_level_list = battle_data.gear_level_list
    gear_mystery_list = battle_data.gear_mystery_list
    sld = battle_data.sld
    # 加点，每点精神或智力有多少护盾
    t_spr_mul = 65
    t_int_mul = 0
    if enemy_data.kf_level >= 300 and 'double-angle-down' not in icon_list[4]:
        t_spr_mul += 13
    if enemy_data.kf_level >= 600 and 'double-angle-down' not in icon_list[4]:
        t_spr_mul += 21
    if enemy_data.kf_level >= 800 and 'angle-up' in icon_list[4]:
        t_spr_mul += 21
    if enemy_data.kf_level >= 1400 and 'double-angle-up' in icon_list[2]:
        t_int_mul += 62
    # 启程心 附加护盾
    xin_ratio = 1 + int(config.read_config('wish_config').split(' ')[3]) * 0.05
    xin_add = xin_ratio * enemy_data.card_level * 10
    # 许愿池 附加护盾
    wish_add = int(config.read_config('wish_config').split(' ')[8]) * 20
    # 装备 附加护盾
    gear_add = 0
    if gear_list[1] == 'BRACELET':
        gear_add += int(gear_level_list[1]) * 20 * int(config.read_config('gear_config')['BRACELET'].split(' ')[2]) / 100
    if gear_list[2] == 'CLOAK':
        gear_add += int(gear_level_list[2]) * 50 * int(config.read_config('gear_config')['CLOAK'].split(' ')[3]) / 100
    if gear_list[2] == 'CAPE':
        gear_add += int(gear_level_list[2]) * 100 * int(config.read_config('gear_config')['CAPE'].split(' ')[1]) / 100
    if gear_list[3] == 'TIARA':
        gear_add += int(gear_level_list[3]) * 20 * int(config.read_config('gear_config')['TIARA'].split(' ')[2]) / 100
    # 装备 百分比护盾
    gear_mul = 1
    if gear_list[2] == 'CLOAK':
        gear_mul *= 1 + ((int(gear_level_list[2]) / 5 + 25) * int(config.read_config('gear_config')['CLOAK'].split(' ')[2]) / 10000)
    if gear_list[2] == 'CAPE':
        gear_mul *= 1 + ((int(gear_level_list[2]) / 5 + 50) * int(config.read_config('gear_config')['CAPE'].split(' ')[0]) / 10000)
    if gear_list[3] == 'TIARA':
        gear_mul *= 1 + (int(gear_level_list[3]) / 5 * int(config.read_config('gear_config')['TIARA'].split(' ')[1]) / 10000)
    # 霞 成长值
    g_add = 0
    if enemy_data.enemy_card == 'XIA':
        g_add += config.read_config('default_g')
    # 最后乘算因素
    final_ratio = 1
    final_ratio += aumlet_from_str(aumlet_str, 'SLD') / 100
    if gear_list[2] == 'CLOAK' and gear_mystery_list[2] == 1:
        final_ratio += 0.5
    if enemy_data.enemy_card == 'MO':
        final_ratio += 0.4
    if enemy_data.enemy_card == 'MENG':
        if gear_list[3] == 'TIARA' and gear_mystery_list[3] == 1:
            final_ratio += 0.45
        else:
            final_ratio += 0.3
    if enemy_data.enemy_card == 'WU':
        final_ratio += 0.3
    # 反推
    base_sld = (sld / final_ratio - g_add - gear_add - wish_add - xin_add) / gear_mul
    if base_sld <= 0:
        attr_data.t_spr = 1
        attr_data.all_point -= 1
        return
    if enemy_data.kf_level >= 1400 and 'double-angle-up' in icon_list[2]:
        if 'double-angle-down' in icon_list[4]:
            attr_data.t_spr = 1
            attr_data.all_point -= 1
            return
        else:
            # 1400系数 智力双上 精神不是双下 默认智力1600
            base_sld -= (t_int_mul * 1600)
            if base_sld < 0:
                attr_data.t_spr = 1
                attr_data.all_point -= 1
                return
    attr_data.t_spr = int(base_sld / t_spr_mul)
    if attr_data.t_spr <= aumlet_from_str(aumlet_str, 'SPR'):
        attr_data.t_spr = 1
        attr_data.all_point -= 1
        return
    # 系数校验
    if enemy_data.kf_level >= 800 and 'angle-up' in icon_list[4] and attr_data.t_spr < 1000:
        attr_data.t_spr = 1000
    elif enemy_data.kf_level >= 600 and 'double-angle-down' not in icon_list[4] and attr_data.t_spr < 500:
        attr_data.t_spr = 500
    elif enemy_data.kf_level >= 300 and 'double-angle-down' not in icon_list[4] and attr_data.t_spr < 200:
        attr_data.t_spr = 200
    attr_data.t_spr -= aumlet_from_str(aumlet_str, 'SPR')
    if attr_data.all_point <= attr_data.t_spr + 5:
        attr_data.t_spr = attr_data.all_point - 5
        attr_data.t_str = 1
        attr_data.t_int = 1
        attr_data.t_agi = 1
        attr_data.t_mnd = 1
        attr_data.t_vit = 1
        attr_data.all_point = 0
        return
    attr_data.all_point -= attr_data.t_spr


# 血量计算
def cal_hp(enemy_data, battle_data, attr_data, aumlet_str):
    if attr_data.all_point == 0:
        return
    icon_list = battle_data.attr_list
    gear_list = battle_data.gear_list
    gear_level_list = battle_data.gear_level_list
    hp = battle_data.hp
    # 加点，每点体意或力量有多少生命
    t_vm_mul = 35
    t_str_mul = 0
    if enemy_data.kf_level >= 300:
        t_vm_mul += 7
    if enemy_data.kf_level >= 600 and ('double-angle-down' not in icon_list[3] or 'double-angle-down' not in icon_list[5]):
        t_vm_mul += 10
    if enemy_data.kf_level >= 800 and ('angle-up' in icon_list[3] or 'angle-up' in icon_list[5]):
        t_vm_mul += 17
    if enemy_data.kf_level >= 1300 and 'double-angle-up' in icon_list[0]:
        t_str_mul += 30
    # 启程心 附加生命
    xin_ratio = 1 + int(config.read_config('wish_config').split(' ')[3]) * 0.05
    xin_add = xin_ratio * enemy_data.card_level * 10
    # 许愿池 附加生命
    wish_add = int(config.read_config('wish_config').split(' ')[7]) * 12
    # 装备 附加生命
    gear_add = 0
    if gear_list[1] == 'GLOVES':
        gear_add += int(gear_level_list[1]) * 10 * int(config.read_config('gear_config')['GLOVES'].split(' ')[3]) / 100
    if gear_list[1] == 'DEVOUR':
        if 'double-angle-up' in icon_list[0]:
            gear_add += 1500 * int(gear_level_list[1]) * 0.08 * int(config.read_config('gear_config')['DEVOUR'].split(' ')[2]) / 100
        elif 'angle-up' in icon_list[0]:
            gear_add += 800 * int(gear_level_list[1]) * 0.08 * int(config.read_config('gear_config')['DEVOUR'].split(' ')[2]) / 100
    if gear_list[2] == 'CLOAK':
        gear_add += int(gear_level_list[2]) * 10 * int(config.read_config('gear_config')['CLOAK'].split(' ')[0]) / 100
    if gear_list[3] == 'SCARF':
        gear_add += int(gear_level_list[3]) * 10 * int(config.read_config('gear_config')['SCARF'].split(' ')[0]) / 100
    if gear_list[3] == 'TIARA':
        gear_add += int(gear_level_list[3]) * 5 * int(config.read_config('gear_config')['TIARA'].split(' ')[0]) / 100
    if gear_list[3] == 'RIBBON':
        if 'double-angle-up' in icon_list[3]:
            gear_add += 1500 * int(gear_level_list[3]) / 30 * int(config.read_config('gear_config')['RIBBON'].split(' ')[2]) / 100
        elif 'angle-up' in icon_list[3]:
            gear_add += 800 * int(gear_level_list[3]) / 30 * int(config.read_config('gear_config')['RIBBON'].split(' ')[2]) / 100
        if 'double-angle-up' in icon_list[5]:
            gear_add += 1500 * int(gear_level_list[3]) / 30 * int(config.read_config('gear_config')['RIBBON'].split(' ')[3]) / 100
        elif 'angle-up' in icon_list[5]:
            gear_add += 800 * int(gear_level_list[3]) / 30 * int(config.read_config('gear_config')['RIBBON'].split(' ')[3]) / 100
    if gear_list[3] == 'HUNT':
        if 'double-angle-up' in icon_list[0]:
            gear_add += 1500 * int(gear_level_list[3]) * 0.08 * int(config.read_config('gear_config')['HUNT'].split(' ')[1]) / 100
        elif 'angle-up' in icon_list[0]:
            gear_add += 800 * int(gear_level_list[3]) * 0.08 * int(config.read_config('gear_config')['HUNT'].split(' ')[1]) / 100
        if 'double-angle-up' in icon_list[1]:
            gear_add += 1500 * int(gear_level_list[3]) * 0.08 * int(config.read_config('gear_config')['HUNT'].split(' ')[2]) / 100
        elif 'angle-up' in icon_list[1]:
            gear_add += 1000 * int(gear_level_list[3]) * 0.08 * int(config.read_config('gear_config')['HUNT'].split(' ')[2]) / 100
    # 装备 百分比生命
    gear_mul = 1
    if gear_list[1] == 'DEVOUR':
        gear_mul *= 1 + int(gear_level_list[1]) * 0.07 * int(config.read_config('gear_config')['DEVOUR'].split(' ')[3]) / 10000
    if gear_list[2] == 'THORN':
        gear_mul *= 1 + ((int(gear_level_list[2]) / 5 + 20) * int(config.read_config('gear_config')['THORN'].split(' ')[0]) / 10000)
    if gear_list[2] == 'WOOD':
        gear_mul *= 1 + ((int(gear_level_list[2]) / 5 + 50) * int(config.read_config('gear_config')['WOOD'].split(' ')[0]) / 10000)
    if gear_list[3] == 'HUNT':
        gear_mul *= 1 + (int(gear_level_list[3]) * 0.06 * int(config.read_config('gear_config')['HUNT'].split(' ')[3]) / 10000)
    # 希 成长值
    g_add = 0
    if enemy_data.enemy_card == 'XI':
        g_add += config.read_config('default_g')
    # 最后乘算因素
    final_ratio = 1
    final_ratio += aumlet_from_str(aumlet_str, 'HP') / 100
    if enemy_data.enemy_card == 'LIN':
        final_ratio += 0.3
    if enemy_data.enemy_card == 'YI':
        final_ratio += 0.2
    if enemy_data.enemy_card == 'XI':
        final_ratio += 0.1
    if enemy_data.enemy_card == 'MING':
        final_ratio += 0.9
    if enemy_data.enemy_card == 'WU':
        final_ratio += 0.3
    # 反推
    base_hp = (hp / final_ratio - g_add - gear_add - wish_add - xin_add) / gear_mul
    if base_hp <= 0:
        attr_data.t_vit = 1
        attr_data.t_mnd = 1
        attr_data.all_point -= 2
        return
    if enemy_data.kf_level >= 1300 and 'double-angle-up' in icon_list[0]:
        # 1300系数 默认力量1500
        base_hp -= t_str_mul * 1500
        if 'double-angle-down' in icon_list[3] and 'double-angle-down' in icon_list[5]:
            attr_data.t_vit = 1
            attr_data.t_mnd = 1
            attr_data.all_point -= 2
            return
        elif 'double-angle-down' in icon_list[3]:
            attr_data.t_vit = 1
            attr_data.all_point -= 1
            attr_data.t_mnd = int(base_hp / t_vm_mul)
            if attr_data.t_mnd <= 0:
                attr_data.t_mnd = 1
            attr_data.all_point -= attr_data.t_mnd
            return
        elif 'double-angle-down' in icon_list[5]:
            attr_data.t_mnd = 1
            attr_data.all_point -= 1
            attr_data.t_vit = int(base_hp / t_vm_mul)
            if attr_data.t_vit <= 0:
                attr_data.t_vit = 1
            attr_data.all_point -= attr_data.t_vit
            return
        else:
            if base_hp <= 0:
                attr_data.t_vit = 1
                attr_data.t_mnd = 1
                attr_data.all_point -= 2
                return
            t_vit_mnd = int(base_hp / t_vm_mul)
            if t_vit_mnd <= 2:
                t_vit_mnd = 2
            attr_data.t_vit = int(t_vit_mnd / 2)
            attr_data.t_mnd = t_vit_mnd - attr_data.t_vit
            attr_data.all_point -= t_vit_mnd
            return
    t_vit_mnd = int(base_hp / t_vm_mul)
    if t_vit_mnd <= (aumlet_from_str(aumlet_str, 'VIT') + aumlet_from_str(aumlet_str, 'MND') + 4):
        attr_data.t_vit = 1
        attr_data.t_mnd = 1
        attr_data.all_point -= 2
        return
    # 系数校验
    if enemy_data.kf_level >= 800 \
            and ('angle-up' in icon_list[3] or 'angle-up' in icon_list[5]) \
            and t_vit_mnd < 1000:
        t_vit_mnd = 1000
    elif enemy_data.kf_level >= 600 and ('double-angle-down' not in icon_list[3] \
            or 'double-angle-down' not in icon_list[5]) and t_vit_mnd < 500:
        t_vit_mnd = 500
    elif enemy_data.kf_level >= 300 and t_vit_mnd > 200:
        t_vit_mnd = 200
    t_vit_mnd -= (aumlet_from_str(aumlet_str, 'VIT') + aumlet_from_str(aumlet_str, 'MND'))
    if attr_data.all_point <= t_vit_mnd + 3:
        t_vit_mnd = attr_data.all_point - 3
        attr_data.t_str = 1
        attr_data.t_int = 1
        attr_data.t_agi = 1
        attr_data.all_point = 0
        # 分体意
        split_vit_mnd(t_vit_mnd, attr_data, icon_list)
        return
    # 分体意
    split_vit_mnd(t_vit_mnd, attr_data, icon_list)
    attr_data.all_point -= t_vit_mnd


# 根据比例图标拆分体意
def split_vit_mnd(t_vit_mnd, attr_data, icon_list):
    if icon_list[3] == icon_list[5]:
        # 平分
        attr_data.t_vit = int(t_vit_mnd / 2)
        attr_data.t_mnd = t_vit_mnd - attr_data.t_vit
        return
    if 'double-angle-down' in icon_list[3]:
        # 全意志
        attr_data.t_vit = 1
        attr_data.t_mnd = t_vit_mnd - 1
        return
    if 'double-angle-down' in icon_list[5]:
        # 全体魄
        attr_data.t_mnd = 1
        attr_data.t_vit = t_vit_mnd - 1
        return
    if ('icon-angle-up' in icon_list[3] and 'double-angle-up' in icon_list[5]) \
        or ('icon-angle-up' in icon_list[5] and 'double-angle-up' in icon_list[3]):
        # 单上 双上 差距不大也平分
        attr_data.t_vit = int(t_vit_mnd / 2)
        attr_data.t_mnd = t_vit_mnd - attr_data.t_vit
        return
    if 'icon-angle-down' in icon_list[3] and 'double-angle-up' in icon_list[5]:
        # 单下 双上 1:3分
        attr_data.t_vit = int(t_vit_mnd / 4)
        attr_data.t_mnd = t_vit_mnd - attr_data.t_vit
        return
    if 'icon-angle-down' in icon_list[5] and 'double-angle-up' in icon_list[3]:
        # 单下 双上 1:3分
        attr_data.t_mnd = int(t_vit_mnd / 4)
        attr_data.t_vit = t_vit_mnd - attr_data.t_mnd
        return
    if 'icon-angle-down' in icon_list[3] and 'icon-angle-up' in icon_list[5]:
        # 单下 单上 1:2分
        attr_data.t_vit = int(t_vit_mnd / 3)
        attr_data.t_mnd = t_vit_mnd - attr_data.t_vit
        return
    if 'icon-angle-down' in icon_list[5] and 'icon-angle-up' in icon_list[3]:
        # 单下 单上 1:2分
        attr_data.t_mnd = int(t_vit_mnd / 3)
        attr_data.t_vit = t_vit_mnd - attr_data.t_mnd
        return


# 从icon中推断敏捷的比例
def agi_ratio(icon):
    if 'double-angle-down' in icon:
        return 0.05
    if 'angle-down' in icon:
        return 0.2
    if 'angle-up' in icon:
        return 0.4


# 从icon中推断智力的比例
def int_ratio(icon):
    if 'double-angle-down' in icon:
        return 0.001
    if 'angle-down' in icon:
        return 0.1
    if 'angle-up' in icon:
        return 0.3
    if 'double-angle-up' in icon:
        return 0.999


# 从字符串中获取护符对应的属性值
def aumlet_from_str(aumlet_str, attr):
    pattern = fr"{attr}\s+(\d+)"
    match = re.search(pattern, aumlet_str)
    if match:
        return int(match.group(1))
    else:
        return 0

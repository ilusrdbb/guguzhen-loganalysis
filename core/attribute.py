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
    # 总点数 包含苹果
    final_apple_point = 0
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
    # 获取包含苹果的总点数
    attr_data.final_apple_point = attr_data.final_point + aumlet_from_str(aumlet_str, 'STR') \
                                  + aumlet_from_str(aumlet_str, 'AGI') \
                                  + aumlet_from_str(aumlet_str, 'INT') \
                                  + aumlet_from_str(aumlet_str, 'VIT') \
                                  + aumlet_from_str(aumlet_str, 'SPR') \
                                  + aumlet_from_str(aumlet_str, 'MND') \
                                  + aumlet_from_str(aumlet_str, 'AAA') * 6
    # 根据血量和护盾 推测意志、精神、体魄
    cal_hp_sld(enemy_data, battle_data, attr_data, aumlet_str)
    # 根据剩余点数和图标大致推断力量、智力、敏捷
    cal_other_attr(battle_data, attr_data, enemy_data, aumlet_str)


# 根据剩余点数和图标大致推断力量、智力、敏捷
def cal_other_attr(battle_data, attr_data, enemy_data, aumlet_str):
    if attr_data.all_point == 0:
        return
    icon_list = battle_data.attr_list
    # 先看速度
    if 'double-angle-up' in icon_list[1]:
        if 'double-angle-up' in icon_list[0] or 'double-angle-up' in icon_list[2]:
            t_agi = int(attr_data.all_point * config.read_config('agi_prop_dudu'))
        elif 'angle-up' in icon_list[0] or 'angle-up' in icon_list[2]:
            t_agi = int(attr_data.all_point * config.read_config('agi_prop_duu'))
        elif 'icon-angle-down' in icon_list[0] or 'icon-angle-down' in icon_list[2]:
            t_agi = int(attr_data.all_point * config.read_config('agi_prop_dud'))
        else:
            # 全敏
            attr_data.t_agi = attr_data.all_point - 2
            attr_data.t_str = 1
            attr_data.t_int = 1
            return
    else:
        t_agi = int(attr_data.final_apple_point * agi_ratio(icon_list[1])) \
                - aumlet_from_str(aumlet_str, 'AGI') - aumlet_from_str(aumlet_str, 'AAA')
    if t_agi == 2 or t_agi < 1:
        t_agi = 1
    if t_agi >= attr_data.all_point - 2:
        attr_data.t_agi = attr_data.all_point - 2
        attr_data.t_str = 1
        attr_data.t_int = 1
        return
    attr_data.t_agi = t_agi
    attr_data.all_point -= t_agi
    # 智力
    t_int = int(attr_data.final_apple_point * int_ratio(icon_list[2])) \
            - aumlet_from_str(aumlet_str, 'INT') - aumlet_from_str(aumlet_str, 'AAA')
    if t_int == 2 or t_int < 1:
        t_int = 1
    if enemy_data.kf_level >= 1400 and 'double-angle-up' in icon_list[2]:
        # 1400 智力校验
        if t_int <= config.read_config('1400_int'):
            t_int = config.read_config('1400_int')
    if t_int >= attr_data.all_point - 1:
        if enemy_data.kf_level >= 1400 and 'double-angle-up' in icon_list[2]:
            # 1400争夺的智力补偿
            # 先从精神拿 然后是敏捷
            diff = config.read_config('1400_int') - attr_data.all_point + 1
            if diff < attr_data.t_spr:
                attr_data.t_spr -= diff
                attr_data.t_int = config.read_config('1400_int')
                attr_data.t_str = 1
                return
            else:
                diff -= (attr_data.t_spr - 1)
                attr_data.t_spr = 1
                attr_data.t_agi -= diff
                attr_data.t_str = 1
                attr_data.t_int = config.read_config('1400_int')
                return
        else:
            # 非1400不补偿，直接榨干剩余点数
            attr_data.t_int = attr_data.all_point - 1
            attr_data.t_str = 1
            return
    attr_data.t_int = t_int
    attr_data.all_point -= t_int
    # 力量
    attr_data.t_str = attr_data.all_point
    if enemy_data.kf_level >= 1300 and 'double-angle-up' in icon_list[0]:
        # 1300争夺的力量补偿
        if attr_data.t_str <= config.read_config('1300_str'):
            attr_data.t_str = config.read_config('1300_str')
            diff = config.read_config('1300_str') - attr_data.all_point
            if attr_data.all_point < config.read_config('1300_str'):
                # 先从敏捷拿 拿到1000点 然后从意志拿
                if attr_data.t_agi > 1000 - aumlet_from_str(aumlet_str, 'AGI') - aumlet_from_str(aumlet_str, 'AAA'):
                    diff2 = attr_data.t_agi + aumlet_from_str(aumlet_str, 'AGI') \
                            + aumlet_from_str(aumlet_str, 'AAA') - 1000
                    if diff2 > diff:
                        attr_data.t_agi -= diff
                    else:
                        attr_data.t_agi = 1000 - aumlet_from_str(aumlet_str, 'AGI') - aumlet_from_str(aumlet_str, 'AAA')
                        diff3 = diff - diff2
                        attr_data.t_mnd -= diff3
                else:
                    # 敏捷不够1000就先从意志拿
                    if diff < attr_data.t_mnd:
                        attr_data.t_mnd -= diff
                    else:
                        diff -= (attr_data.t_mnd - 1)
                        attr_data.t_mnd = 1
                        attr_data.t_agi -= diff
        # 1300争夺多余的力量全匀到意志
        if attr_data.t_str > config.read_config('1300_str'):
            diff = attr_data.t_str - config.read_config('1300_str')
            attr_data.t_str = config.read_config('1300_str')
            attr_data.t_mnd += diff
    # 最终点数补偿 找箭头最高的补偿
    if 'double-angle-down' in icon_list[0]:
        finally_add_point(attr_data, icon_list)


# 最终补偿
def finally_add_point(attr_data, icon_list):
    # 多余的点数
    add_point = attr_data.all_point - 1
    # 找双上箭头
    if 'double-angle-up' in icon_list[1]:
        attr_data.t_agi += add_point
        attr_data.t_str = 1
        return
    if 'double-angle-up' in icon_list[2]:
        attr_data.t_int += add_point
        attr_data.t_str = 1
        return
    if 'double-angle-up' in icon_list[4]:
        attr_data.t_spr += add_point
        attr_data.t_str = 1
        return
    if 'double-angle-up' in icon_list[5]:
        attr_data.t_mnd += add_point
        attr_data.t_str = 1
        return
    if 'double-angle-up' in icon_list[3]:
        attr_data.t_vit += add_point
        attr_data.t_str = 1
        return
    # 找单上
    if 'icon-angle-up' in icon_list[1]:
        attr_data.t_agi += add_point
        attr_data.t_str = 1
        return
    if 'icon-angle-up' in icon_list[4]:
        attr_data.t_spr += add_point
        attr_data.t_str = 1
        return
    if 'icon-angle-up' in icon_list[5]:
        attr_data.t_mnd += add_point
        attr_data.t_str = 1
        return
    if 'icon-angle-up' in icon_list[3]:
        attr_data.t_vit += add_point
        attr_data.t_str = 1
        return
    if 'icon-angle-up' in icon_list[2]:
        attr_data.t_int += add_point
        attr_data.t_str = 1
        return


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
    # 精神双下直接返回1点
    if 'double-angle-down' in icon_list[4]:
        attr_data.t_spr = 1
        attr_data.all_point -= 1
        return
    # 加点，每点精神或智力有多少护盾
    t_spr_mul = 65
    t_int_mul = 0
    if enemy_data.kf_level >= 300:
        t_spr_mul += 13
    if enemy_data.kf_level >= 600 and 'double-angle-down' not in icon_list[2]:
        # 单上/双上
        t_spr_mul += 21
    if enemy_data.kf_level >= 800 and 'angle-up' in icon_list[4]:
        # 双上
        t_spr_mul += 32
    if enemy_data.kf_level >= 1400 and 'double-angle-up' in icon_list[2]:
        t_int_mul += 45
    # 启程心 附加护盾
    xin_ratio = 0
    if 'XIN' in battle_data.talent_list:
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
        # 1400系数 智力双上 精神不是双下
        base_sld -= (t_int_mul * config.read_config('1400_int'))
        if base_sld < 0:
            attr_data.t_spr = 1
            attr_data.all_point -= 1
            return
    attr_data.t_spr = int(base_sld / t_spr_mul)
    if attr_data.t_spr <= aumlet_from_str(aumlet_str, 'SPR') + aumlet_from_str(aumlet_str, 'AAA'):
        attr_data.t_spr = 1
        attr_data.all_point -= 1
        return
    # 箭头校验
    attr_data.t_spr = icon_check(attr_data.t_spr, attr_data.final_apple_point, icon_list[4])
    attr_data.t_spr -= (aumlet_from_str(aumlet_str, 'SPR') + aumlet_from_str(aumlet_str, 'AAA'))
    if attr_data.final_point <= attr_data.t_spr + 5:
        attr_data.t_spr = attr_data.final_point - 5
        attr_data.t_str = 1
        attr_data.t_int = 1
        attr_data.t_agi = 1
        attr_data.t_mnd = 1
        attr_data.t_vit = 1
        attr_data.all_point = 0
        return
    attr_data.all_point -= attr_data.t_spr


# 箭头校验
def icon_check(attr_point, final_apple_point, icon_str):
    if 'double-angle-up' in icon_str:
        # 双上
        if attr_point < int(final_apple_point * 0.4) + 1:
            return int(final_apple_point * 0.4) + 1
    if 'icon-angle-up' in icon_str:
        # 单上
        if attr_point < int(final_apple_point * 0.2) + 1:
            return int(final_apple_point * 0.2) + 1
        if attr_point > int(final_apple_point * 0.4):
            return int(final_apple_point * 0.4)
    if 'icon-angle-down' in icon_str:
        # 单下
        if attr_point < int(final_apple_point * 0.1) + 1:
            return int(final_apple_point * 0.1) + 1
        if attr_point > int(final_apple_point * 0.2):
            return int(final_apple_point * 0.2)
    if 'double-angle-down' in icon_str:
        # 双下
        if attr_point > int(final_apple_point * 0.1):
            return int(final_apple_point * 0.1)
    return attr_point


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
    if enemy_data.kf_level >= 600:
        t_vm_mul += 10
    if enemy_data.kf_level >= 800 \
            and not ('double-angle-down' in icon_list[3] and 'double-angle-down' in icon_list[5]) \
            and not ('double-angle-down' in icon_list[5] and 'icon-angle-down' in icon_list[3]) \
            and not ('double-angle-down' in icon_list[3] and 'icon-angle-down' in icon_list[5]):
        # 不是双下+双下和双下+单下和单下+单下
        t_vm_mul += 17
    if enemy_data.kf_level >= 1300 and 'double-angle-up' in icon_list[0]:
        t_str_mul += 30
    # 启程心 附加生命
    xin_ratio = 0
    if 'XIN' in battle_data.talent_list:
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
        elif 'icon-angle-down' in icon_list[0]:
            gear_add += 500 * int(gear_level_list[1]) * 0.08 * int(config.read_config('gear_config')['DEVOUR'].split(' ')[2]) / 100
    if gear_list[2] == 'CLOAK':
        gear_add += int(gear_level_list[2]) * 10 * int(config.read_config('gear_config')['CLOAK'].split(' ')[0]) / 100
    if gear_list[3] == 'SCARF':
        gear_add += int(gear_level_list[3]) * 10 * int(config.read_config('gear_config')['SCARF'].split(' ')[0]) / 100
    if gear_list[3] == 'TIARA':
        gear_add += int(gear_level_list[3]) * 5 * int(config.read_config('gear_config')['TIARA'].split(' ')[0]) / 100
    if gear_list[3] == 'RIBBON':
        if 'double-angle-up' in icon_list[3]:
            gear_add += 1200 * int(gear_level_list[3]) / 30 * int(config.read_config('gear_config')['RIBBON'].split(' ')[2]) / 100
        elif 'angle-up' in icon_list[3]:
            gear_add += 800 * int(gear_level_list[3]) / 30 * int(config.read_config('gear_config')['RIBBON'].split(' ')[2]) / 100
        elif 'icon-angle-down' in icon_list[3]:
            gear_add += 500 * int(gear_level_list[3]) / 30 * int(config.read_config('gear_config')['RIBBON'].split(' ')[2]) / 100
        if 'double-angle-up' in icon_list[5]:
            gear_add += 1200 * int(gear_level_list[3]) / 30 * int(config.read_config('gear_config')['RIBBON'].split(' ')[3]) / 100
        elif 'angle-up' in icon_list[5]:
            gear_add += 800 * int(gear_level_list[3]) / 30 * int(config.read_config('gear_config')['RIBBON'].split(' ')[3]) / 100
        elif 'icon-angle-down' in icon_list[5]:
            gear_add += 500 * int(gear_level_list[3]) / 30 * int(config.read_config('gear_config')['RIBBON'].split(' ')[3]) / 100
    if gear_list[3] == 'HUNT':
        if 'double-angle-up' in icon_list[0]:
            gear_add += 1500 * int(gear_level_list[3]) * 0.08 * int(config.read_config('gear_config')['HUNT'].split(' ')[1]) / 100
        elif 'angle-up' in icon_list[0]:
            gear_add += 800 * int(gear_level_list[3]) * 0.08 * int(config.read_config('gear_config')['HUNT'].split(' ')[1]) / 100
        elif 'icon-angle-down' in icon_list[0]:
            gear_add += 500 * int(gear_level_list[3]) * 0.08 * int(config.read_config('gear_config')['HUNT'].split(' ')[1]) / 100
        if 'double-angle-up' in icon_list[1]:
            gear_add += 2000 * int(gear_level_list[3]) * 0.08 * int(config.read_config('gear_config')['HUNT'].split(' ')[2]) / 100
        elif 'angle-up' in icon_list[1]:
            gear_add += 1000 * int(gear_level_list[3]) * 0.08 * int(config.read_config('gear_config')['HUNT'].split(' ')[2]) / 100
        elif 'icon-angle-down' in icon_list[1]:
            gear_add += 500 * int(gear_level_list[3]) * 0.08 * int(config.read_config('gear_config')['HUNT'].split(' ')[2]) / 100
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
        # 1300系数
        base_hp -= t_str_mul * config.read_config('1300_str')
        if 'double-angle-down' in icon_list[3] and 'double-angle-down' in icon_list[5]:
            # 全双下 默认给意志体魄一点点
            attr_data.t_vit = 1
            attr_data.all_point -= 1
            attr_data.t_mnd = 1
            if attr_data.all_point > config.read_config('1300_low_wm'):
                attr_data.t_mnd = config.read_config('1300_low_wm')
            attr_data.all_point -= attr_data.t_mnd
            if attr_data.all_point > config.read_config('1300_low_wm'):
                attr_data.t_vit = config.read_config('1300_low_wm')
            attr_data.all_point -= attr_data.t_vit
            return
        elif 'double-angle-down' in icon_list[3]:
            # 一边双下 全匀给另一边
            attr_data.t_mnd = int(base_hp / t_vm_mul) - aumlet_from_str(aumlet_str, 'VIT') \
                              - aumlet_from_str(aumlet_str, 'MND') - aumlet_from_str(aumlet_str, 'AAA') * 2
            if attr_data.t_mnd < int(attr_data.final_apple_point / 10):
                attr_data.t_mnd = int(attr_data.final_apple_point / 10)
            if attr_data.t_mnd < 1:
                attr_data.t_mnd = 1
            attr_data.all_point -= attr_data.t_mnd
            # 追求500点体意的效果
            add_point = 500 - aumlet_from_str(aumlet_str, 'VIT')- aumlet_from_str(aumlet_str, 'MND') \
                        - aumlet_from_str(aumlet_str, 'AAA') * 2 - attr_data.t_mnd
            if add_point < 1:
                attr_data.t_vit = 1
                attr_data.all_point -= 1
            else:
                attr_data.t_vit = add_point
                attr_data.all_point -= add_point
            return
        elif 'double-angle-down' in icon_list[5]:
            # 一边双下 全匀给另一边
            attr_data.t_vit = int(base_hp / t_vm_mul) - aumlet_from_str(aumlet_str, 'VIT') \
                              - aumlet_from_str(aumlet_str, 'MND') - aumlet_from_str(aumlet_str, 'AAA') * 2
            if attr_data.t_vit < int(attr_data.final_apple_point / 10):
                attr_data.t_vit = int(attr_data.final_apple_point / 10)
            if attr_data.t_vit < 1:
                attr_data.t_vit = 1
            attr_data.all_point -= attr_data.t_vit
            # 追求500点体意的效果
            add_point = 500 - aumlet_from_str(aumlet_str, 'VIT') - aumlet_from_str(aumlet_str, 'MND') \
                        - aumlet_from_str(aumlet_str, 'AAA') * 2 - attr_data.t_vit
            if add_point < 1:
                attr_data.t_mnd = 1
                attr_data.all_point -= 1
            else:
                attr_data.t_mnd = add_point
                attr_data.all_point -= add_point
            return
        else:
            # 暴力均分 反正剩余点数也不多
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
    if t_vit_mnd <= (aumlet_from_str(aumlet_str, 'VIT') + aumlet_from_str(aumlet_str, 'MND')
                     + aumlet_from_str(aumlet_str, 'AAA') * 2 + 4):
        attr_data.t_vit = 1
        attr_data.t_mnd = 1
        attr_data.all_point -= 2
        return
    if attr_data.all_point <= t_vit_mnd + 3:
        t_vit_mnd = attr_data.all_point - 3
        attr_data.t_str = 1
        attr_data.t_int = 1
        attr_data.t_agi = 1
        attr_data.all_point = 0
        # 分体意
        split_vit_mnd(t_vit_mnd, attr_data, icon_list)
        return
    # 800争夺 1000点校验
    if 1000 > t_vit_mnd > 800 and enemy_data.kf_level >= 800 \
            and not ('double-angle-down' in icon_list[3] and 'double-angle-down' in icon_list[5]) \
            and not ('double-angle-down' in icon_list[5] and 'icon-angle-down' in icon_list[3]) \
            and not ('double-angle-down' in icon_list[3] and 'icon-angle-down' in icon_list[5]):
        t_vit_mnd = 1000
    # 分体意
    split_vit_mnd(t_vit_mnd, attr_data, icon_list)
    # 箭头校验
    attr_data.t_vit = icon_check(attr_data.t_vit, attr_data.final_apple_point, icon_list[3])
    attr_data.t_vit -= (aumlet_from_str(aumlet_str, 'VIT') + aumlet_from_str(aumlet_str, 'AAA'))
    if attr_data.t_vit < 1:
        attr_data.t_vit = 1
    attr_data.t_mnd = icon_check(attr_data.t_mnd, attr_data.final_apple_point, icon_list[5])
    attr_data.t_mnd -= (aumlet_from_str(aumlet_str, 'MND') + aumlet_from_str(aumlet_str, 'AAA'))
    if attr_data.t_mnd < 1:
        attr_data.t_mnd = 1
    attr_data.all_point -= (attr_data.t_vit + attr_data.t_mnd)


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
    if 'icon-angle-up' in icon_list[3] and 'double-angle-up' in icon_list[5]:
        # 单上 双上
        attr_data.t_mnd = int(t_vit_mnd * config.read_config('vm_prop_udu'))
        attr_data.t_vit = t_vit_mnd - attr_data.t_mnd
        return
    if 'icon-angle-up' in icon_list[5] and 'double-angle-up' in icon_list[3]:
        # 单上 双上
        attr_data.t_vit = int(t_vit_mnd * config.read_config('vm_prop_udu'))
        attr_data.t_mnd = t_vit_mnd - attr_data.t_vit
        return
    if 'icon-angle-down' in icon_list[3] and 'double-angle-up' in icon_list[5]:
        # 单下 双上
        attr_data.t_mnd = int(t_vit_mnd * config.read_config('vm_prop_ddu'))
        attr_data.t_vit = t_vit_mnd - attr_data.t_mnd
        return
    if 'icon-angle-down' in icon_list[5] and 'double-angle-up' in icon_list[3]:
        # 单下 双上
        attr_data.t_vit = int(t_vit_mnd * config.read_config('vm_prop_ddu'))
        attr_data.t_mnd = t_vit_mnd - attr_data.t_vit
        return
    if 'icon-angle-down' in icon_list[3] and 'icon-angle-up' in icon_list[5]:
        # 单下 单上
        attr_data.t_mnd = int(t_vit_mnd * config.read_config('vm_prop_du'))
        attr_data.t_vit = t_vit_mnd - attr_data.t_mnd
        return
    if 'icon-angle-down' in icon_list[5] and 'icon-angle-up' in icon_list[3]:
        # 单下 单上
        attr_data.t_vit = int(t_vit_mnd * config.read_config('vm_prop_du'))
        attr_data.t_mnd = t_vit_mnd - attr_data.t_vit
        return


# 从icon中推断敏捷的比例
def agi_ratio(icon):
    if 'double-angle-down' in icon:
        return config.read_config('agi_prop_dd')
    if 'angle-down' in icon:
        return config.read_config('agi_prop_d')
    if 'angle-up' in icon:
        return config.read_config('agi_prop_u')


# 从icon中推断智力的比例
def int_ratio(icon):
    if 'double-angle-down' in icon:
        return config.read_config('int_prop_dd')
    if 'angle-down' in icon:
        return config.read_config('int_prop_d')
    if 'angle-up' in icon:
        return config.read_config('int_prop_u')
    if 'double-angle-up' in icon:
        return config.read_config('int_prop_du')


# 从字符串中获取护符对应的属性值
def aumlet_from_str(aumlet_str, attr):
    pattern = fr"{attr}\s+(\d+)"
    match = re.search(pattern, aumlet_str)
    if match:
        return int(match.group(1))
    else:
        return 0

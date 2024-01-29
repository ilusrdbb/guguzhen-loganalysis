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
    # 双下-单下边界点
    point_down = 0
    # 单下-单上边界点
    point_up = 0
    # 单上-双上边界点
    point_double_up = 0

    # 初始化
    def __init__(self, enemy):
        if enemy:
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
    # 边界点数
    attr_data.point_down = int(attr_data.final_apple_point * 0.1)
    attr_data.point_up = int(attr_data.final_apple_point * 0.2)
    attr_data.point_double_up = int(attr_data.final_apple_point * 0.4)
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
        # 速度双上
        if 'double-angle-up' in icon_list[0] or 'double-angle-up' in icon_list[2]:
            # 智力/力量 双上
            t_agi = int(attr_data.all_point * config.read_config('agi_prop_dudu'))
        elif 'angle-up' in icon_list[0] or 'angle-up' in icon_list[2]:
            # 智力/力量 单上
            t_agi = int(attr_data.all_point * config.read_config('agi_prop_duu'))
        elif 'icon-angle-down' in icon_list[0] or 'icon-angle-down' in icon_list[2]:
            # 智力/力量 单下
            t_agi = int(attr_data.all_point * config.read_config('agi_prop_dud'))
        else:
            # 智力/力量 双下 全敏
            attr_data.t_agi = attr_data.all_point - 2
            attr_data.t_str = 1
            attr_data.t_int = 1
            return
    else:
        t_agi = int(attr_data.final_apple_point * agi_ratio(icon_list[1])) \
                - aumlet_from_str(aumlet_str, 'AGI') - aumlet_from_str(aumlet_str, 'AAA')
    # 点数正数校验
    if t_agi == 2 or t_agi < 1:
        t_agi = 1
    # 点数溢出校验
    if t_agi >= attr_data.all_point - 2:
        attr_data.t_agi = attr_data.all_point - 2
        attr_data.t_str = 1
        attr_data.t_int = 1
        return
    attr_data.t_agi = t_agi
    attr_data.all_point -= t_agi
    # 再看智力
    t_int = int(attr_data.final_apple_point * int_ratio(icon_list[2])) \
            - aumlet_from_str(aumlet_str, 'INT') - aumlet_from_str(aumlet_str, 'AAA')
    # 点数正数校验
    if t_int == 2 or t_int < 1:
        t_int = 1
    if t_int >= attr_data.all_point - 1:
        # 直接榨干剩余点数
        attr_data.t_int = attr_data.all_point - 1
        attr_data.t_str = 1
        return
    attr_data.t_int = t_int
    attr_data.all_point -= t_int
    # 最后看力量
    attr_data.t_str = attr_data.all_point
    if attr_data.t_str < 1:
        attr_data.t_str = 1
    # 缺少点数补偿
    if attr_data.all_point <= 0:
        lost_point = attr_data.t_str + attr_data.t_agi + attr_data.t_int \
                     + attr_data.t_vit + attr_data.t_spr + attr_data.t_mnd \
                     - attr_data.final_point
        lost_point_compensation(lost_point, icon_list, attr_data, aumlet_str)
    # 双下力量的多余点数补偿
    if 'double-angle-down' in icon_list[0]:
        left_point = attr_data.t_str - 1
        attr_data.t_str = 1
        left_point_compensation(left_point, icon_list, attr_data, aumlet_str)
    # 单下力量的多余点数补偿
    if 'icon-angle-down' in icon_list[0] and attr_data.t_str > int(attr_data.final_apple_point * 0.2):
        left_point = attr_data.t_str - int(attr_data.final_apple_point * 0.2)
        attr_data.t_str = int(attr_data.final_apple_point * 0.2)
        left_point_compensation(left_point, icon_list, attr_data, aumlet_str)


# 缺少点数补偿 由于只会存在于1300和1400时，写的比较死，先这样
def lost_point_compensation(lost_point, icon_list, attr_data, aumlet_str):
    _lost_point = lost_point
    # 先从敏捷补，上箭头补到敏捷剩1000，下箭头补到箭头上限
    if 'angle-up' in icon_list[1] and attr_data.t_agi > 1000 \
            - aumlet_from_str(aumlet_str, 'AGI') - aumlet_from_str(aumlet_str, 'AAA'):
        new_agi = 1000 - aumlet_from_str(aumlet_str, 'AGI') - aumlet_from_str(aumlet_str, 'AAA')
        diff_point = attr_data.t_agi - new_agi
        attr_data.t_agi = new_agi
        if diff_point >= _lost_point:
            return
        _lost_point -= diff_point
    else:
        new_agi = attr_data.t_agi - _lost_point
        if new_agi < 1:
            _lost_point -= (attr_data.t_agi - 1)
            attr_data.t_agi = 1
        else:
            check_value = icon_check_amulet(new_agi, attr_data.final_apple_point, icon_list[1], aumlet_str, 't_agi')
            if check_value <= new_agi:
                attr_data.t_agi = new_agi
                return
            attr_data.t_agi = check_value
            _lost_point = check_value - new_agi
    # 排序精体意
    attr_name_list = sort_attr_list(attr_data)
    # 找精体意最高的属性补
    most_attr_name = attr_name_list[0]
    most_attr_value = getattr(attr_data, most_attr_name) - _lost_point
    icon_str = get_icon_str(icon_list, most_attr_name)
    if most_attr_value < 1:
        _lost_point -= (getattr(attr_data, most_attr_name) - 1)
        setattr(attr_data, most_attr_name, 1)
    else:
        check_value = icon_check_amulet(most_attr_value, attr_data.final_apple_point, icon_str, aumlet_str,
                                        most_attr_name)
        if check_value <= most_attr_value:
            setattr(attr_data, most_attr_name, most_attr_value)
            return
        setattr(attr_data, most_attr_name, check_value)
        _lost_point = check_value - most_attr_value
    # 找次高的补 补完出现负数从敏捷补
    more_attr_name = attr_name_list[1]
    more_attr_value = getattr(attr_data, more_attr_name) - _lost_point
    if more_attr_value > 0:
        setattr(attr_data, more_attr_name, more_attr_value)
    else:
        attr_data.t_agi -= _lost_point


# 排序精体意 返回属性名list
def sort_attr_list(attr_data):
    attr_list = ['t_vit', 't_spr', 't_mnd']
    attr_list.sort(key=lambda attr: getattr(attr_data, attr), reverse=True)
    return attr_list


# 多余点数补偿
def left_point_compensation(left_point, icon_list, attr_data, aumlet_str):
    _left_point = left_point
    _check_point = 0
    # 需要补偿的属性列表
    compensation_attr_list = get_compensation_attr_list(icon_list)
    if compensation_attr_list:
        # 平分
        avg_point = int(_left_point / len(compensation_attr_list))
        for attr_name in compensation_attr_list:
            attr_value = getattr(attr_data, attr_name) + avg_point
            setattr(attr_data, attr_name, attr_value)
            _left_point -= avg_point
            # 校验
            icon_str = get_icon_str(icon_list, attr_name)
            check_value = icon_check_amulet(attr_value, attr_data.final_apple_point, icon_str, aumlet_str, attr_name)
            if check_value < attr_value:
                # 没通过校验的处理
                setattr(attr_data, attr_name, check_value)
                _check_point += attr_value - check_value
    # 最后剩余的点数全扔力量
    attr_data.t_str += _left_point + _check_point


# 根据属性名获取箭头
def get_icon_str(icon_list, attr_name):
    if attr_name == 't_str':
        return icon_list[0]
    if attr_name == 't_agi':
        return icon_list[1]
    if attr_name == 't_int':
        return icon_list[2]
    if attr_name == 't_vit':
        return icon_list[3]
    if attr_name == 't_spr':
        return icon_list[4]
    if attr_name == 't_mnd':
        return icon_list[5]
    return None


# 获取需要补偿的属性列表
def get_compensation_attr_list(icon_list):
    result_list = []
    # 找双上箭头 优先智力和敏捷
    if 'double-angle-up' in icon_list[1]:
        result_list.append('t_agi')
    if 'double-angle-up' in icon_list[2]:
        result_list.append('t_int')
    if 'icon-angle-up' in icon_list[1]:
        result_list.append('t_agi')
    if 'icon-angle-up' in icon_list[2]:
        result_list.append('t_int')
    # 如果智力和敏捷没有再找其他的
    if not result_list:
        if 'double-angle-up' in icon_list[3]:
            result_list.append('t_vit')
        if 'double-angle-up' in icon_list[4]:
            result_list.append('t_spr')
        if 'double-angle-up' in icon_list[5]:
            result_list.append('t_mnd')
        if 'icon-angle-up' in icon_list[3]:
            result_list.append('t_vit')
        if 'icon-angle-up' in icon_list[4]:
            result_list.append('t_spr')
        if 'icon-angle-up' in icon_list[5]:
            result_list.append('t_mnd')
    return result_list


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
    kf_level = enemy_data.kf_level
    if kf_level >= 2000:
        kf_level = 2000
    t_spr_mul = 65 + int(kf_level / 100) * 3.4
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
        gear_add += int(gear_level_list[1]) * 20 * int(
            config.read_config('gear_config')['BRACELET'].split(' ')[2]) / 100
    if gear_list[2] == 'CLOAK':
        gear_add += int(gear_level_list[2]) * 50 * int(config.read_config('gear_config')['CLOAK'].split(' ')[3]) / 100
    if gear_list[2] == 'CAPE':
        gear_add += int(gear_level_list[2]) * 100 * int(config.read_config('gear_config')['CAPE'].split(' ')[1]) / 100
    if gear_list[3] == 'TIARA':
        gear_add += int(gear_level_list[3]) * 20 * int(config.read_config('gear_config')['TIARA'].split(' ')[2]) / 100
    # 装备 百分比护盾
    gear_mul = 1
    if gear_list[2] == 'CLOAK':
        gear_mul += (int(gear_level_list[2]) / 5 + 25) * int(
            config.read_config('gear_config')['CLOAK'].split(' ')[2]) / 10000
    if gear_list[2] == 'CAPE':
        gear_mul += (int(gear_level_list[2]) / 5 + 50) * int(
            config.read_config('gear_config')['CAPE'].split(' ')[0]) / 10000
    if gear_list[3] == 'TIARA':
        gear_mul += int(gear_level_list[3]) / 5 * int(config.read_config('gear_config')['TIARA'].split(' ')[1]) / 10000
    # 霞 成长值
    g_add = 0
    if enemy_data.enemy_card == 'XIA':
        g_add += config.read_config('default_g')
    # 最后乘算因素
    final_ratio = 1
    final_ratio += aumlet_from_str(aumlet_str, 'SLD') / 100
    if gear_list[2] == 'CLOAK' and gear_mystery_list[2] == '1':
        final_ratio += 0.5
    if enemy_data.enemy_card == 'MO':
        final_ratio += 0.4
    if enemy_data.enemy_card == 'MENG':
        if gear_list[3] == 'TIARA' and gear_mystery_list[3] == '1':
            final_ratio += 0.45
        else:
            final_ratio += 0.3
    if enemy_data.enemy_card == 'WU':
        final_ratio += 0.3
    # 反推
    base_sld = (sld / final_ratio - g_add - gear_add - wish_add - xin_add) / gear_mul
    attr_data.t_spr = int(base_sld / t_spr_mul)
    # 箭头校验
    attr_data.t_spr = icon_check(attr_data.t_spr, attr_data.final_apple_point, icon_list[4])
    # 点数正数校验
    if attr_data.t_spr <= aumlet_from_str(aumlet_str, 'SPR') + aumlet_from_str(aumlet_str, 'AAA'):
        attr_data.t_spr = 1
        attr_data.all_point -= 1
        return
    attr_data.t_spr -= (aumlet_from_str(aumlet_str, 'SPR') + aumlet_from_str(aumlet_str, 'AAA'))
    # 点数溢出校验
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


# 箭头校验 返回不包含苹果的数值
def icon_check_amulet(attr_point, final_apple_point, icon_str, aumlet_str, attr_name):
    # 通过属性名获取苹果名
    aumlet_name = ''
    if attr_name == 't_str':
        aumlet_name = 'STR'
    if attr_name == 't_int':
        aumlet_name = 'INT'
    if attr_name == 't_agi':
        aumlet_name = 'AGI'
    if attr_name == 't_vit':
        aumlet_name = 'VIT'
    if attr_name == 't_spr':
        aumlet_name = 'SPR'
    if attr_name == 't_mnd':
        aumlet_name = 'MND'
    aumlet_value = aumlet_from_str(aumlet_str, aumlet_name) + aumlet_from_str(aumlet_str, 'AAA')
    if 'double-angle-up' in icon_str:
        # 双上
        if attr_point < int(final_apple_point * 0.4) + 1:
            return int(final_apple_point * 0.4) + 1 - aumlet_value
    if 'icon-angle-up' in icon_str:
        # 单上
        if attr_point < int(final_apple_point * 0.2) + 1:
            return int(final_apple_point * 0.2) + 1 - aumlet_value
        if attr_point > int(final_apple_point * 0.4):
            return int(final_apple_point * 0.4) - aumlet_value
    if 'icon-angle-down' in icon_str:
        # 单下
        if attr_point < int(final_apple_point * 0.1) + 1:
            return int(final_apple_point * 0.1) + 1 - aumlet_value
        if attr_point > int(final_apple_point * 0.2):
            return int(final_apple_point * 0.2) - aumlet_value
    if 'double-angle-down' in icon_str:
        # 双下
        if attr_point > int(final_apple_point * 0.1):
            return int(final_apple_point * 0.1) - aumlet_value
    return attr_point


# 箭头校验 返回包含苹果的数值
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
    # 加点，每点体意有多少生命
    kf_level = enemy_data.kf_level
    if kf_level >= 2000:
        kf_level = 2000
    t_vm_mul = 35 + int(kf_level / 100) * 1.7
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
            gear_add += 1500 * int(gear_level_list[1]) * 0.08 * int(
                config.read_config('gear_config')['DEVOUR'].split(' ')[2]) / 100
        elif 'angle-up' in icon_list[0]:
            gear_add += 800 * int(gear_level_list[1]) * 0.08 * int(
                config.read_config('gear_config')['DEVOUR'].split(' ')[2]) / 100
        elif 'icon-angle-down' in icon_list[0]:
            gear_add += 500 * int(gear_level_list[1]) * 0.08 * int(
                config.read_config('gear_config')['DEVOUR'].split(' ')[2]) / 100
    if gear_list[2] == 'CLOAK':
        gear_add += int(gear_level_list[2]) * 10 * int(config.read_config('gear_config')['CLOAK'].split(' ')[0]) / 100
    if gear_list[3] == 'SCARF':
        gear_add += int(gear_level_list[3]) * 10 * int(config.read_config('gear_config')['SCARF'].split(' ')[0]) / 100
    if gear_list[3] == 'TIARA':
        gear_add += int(gear_level_list[3]) * 5 * int(config.read_config('gear_config')['TIARA'].split(' ')[0]) / 100
    if gear_list[3] == 'RIBBON':
        if 'double-angle-up' in icon_list[3]:
            gear_add += 1200 * int(gear_level_list[3]) / 30 * int(
                config.read_config('gear_config')['RIBBON'].split(' ')[2]) / 100
        elif 'angle-up' in icon_list[3]:
            gear_add += 800 * int(gear_level_list[3]) / 30 * int(
                config.read_config('gear_config')['RIBBON'].split(' ')[2]) / 100
        elif 'icon-angle-down' in icon_list[3]:
            gear_add += 500 * int(gear_level_list[3]) / 30 * int(
                config.read_config('gear_config')['RIBBON'].split(' ')[2]) / 100
        if 'double-angle-up' in icon_list[5]:
            gear_add += 1200 * int(gear_level_list[3]) / 30 * int(
                config.read_config('gear_config')['RIBBON'].split(' ')[3]) / 100
        elif 'angle-up' in icon_list[5]:
            gear_add += 800 * int(gear_level_list[3]) / 30 * int(
                config.read_config('gear_config')['RIBBON'].split(' ')[3]) / 100
        elif 'icon-angle-down' in icon_list[5]:
            gear_add += 500 * int(gear_level_list[3]) / 30 * int(
                config.read_config('gear_config')['RIBBON'].split(' ')[3]) / 100
    if gear_list[3] == 'HUNT':
        if 'double-angle-up' in icon_list[0]:
            gear_add += 1500 * int(gear_level_list[3]) * 0.08 * int(
                config.read_config('gear_config')['HUNT'].split(' ')[1]) / 100
        elif 'angle-up' in icon_list[0]:
            gear_add += 800 * int(gear_level_list[3]) * 0.08 * int(
                config.read_config('gear_config')['HUNT'].split(' ')[1]) / 100
        elif 'icon-angle-down' in icon_list[0]:
            gear_add += 500 * int(gear_level_list[3]) * 0.08 * int(
                config.read_config('gear_config')['HUNT'].split(' ')[1]) / 100
        if 'double-angle-up' in icon_list[1]:
            gear_add += 2500 * int(gear_level_list[3]) * 0.08 * int(
                config.read_config('gear_config')['HUNT'].split(' ')[2]) / 100
        elif 'angle-up' in icon_list[1]:
            gear_add += 1000 * int(gear_level_list[3]) * 0.08 * int(
                config.read_config('gear_config')['HUNT'].split(' ')[2]) / 100
        elif 'icon-angle-down' in icon_list[1]:
            gear_add += 500 * int(gear_level_list[3]) * 0.08 * int(
                config.read_config('gear_config')['HUNT'].split(' ')[2]) / 100
    # 装备 百分比生命
    gear_mul = 1
    if gear_list[1] == 'DEVOUR':
        gear_mul += int(gear_level_list[1]) * 0.07 * int(
            config.read_config('gear_config')['DEVOUR'].split(' ')[3]) / 10000
    if gear_list[2] == 'THORN':
        gear_mul += (int(gear_level_list[2]) / 5 + 20) * int(
            config.read_config('gear_config')['THORN'].split(' ')[0]) / 10000
    if gear_list[2] == 'WOOD':
        gear_mul += (int(gear_level_list[2]) / 5 + 50) * int(
            config.read_config('gear_config')['WOOD'].split(' ')[0]) / 10000
    if gear_list[3] == 'HUNT':
        gear_mul += int(gear_level_list[3]) * 0.06 * int(
            config.read_config('gear_config')['HUNT'].split(' ')[3]) / 10000
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
    t_vit_mnd = int(base_hp / t_vm_mul)
    # 正数校验
    if t_vit_mnd <= (aumlet_from_str(aumlet_str, 'VIT') + aumlet_from_str(aumlet_str, 'MND')
                    + aumlet_from_str(aumlet_str, 'AAA') * 2 + 4):
        attr_data.t_vit = 1
        attr_data.t_mnd = 1
        attr_data.all_point -= 2
        return
    # 点数溢出校验
    if attr_data.all_point <= t_vit_mnd + 3:
        t_vit_mnd = attr_data.all_point - 3
        attr_data.t_str = 1
        attr_data.t_int = 1
        attr_data.t_agi = 1
        attr_data.all_point = 0
        # 分体意
        split_vit_mnd(t_vit_mnd, attr_data, icon_list, aumlet_str)
        return
    # 分体意
    split_vit_mnd(t_vit_mnd, attr_data, icon_list, aumlet_str)
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
def split_vit_mnd(t_vit_mnd, attr_data, icon_list, aumlet_str):
    if icon_list[3] == icon_list[5]:
        # 平分
        attr_data.t_vit = int(t_vit_mnd / 2)
        attr_data.t_mnd = t_vit_mnd - attr_data.t_vit
        return
    if 'double-angle-down' in icon_list[3]:
        # 全意志
        attr_data.t_vit = 1 + aumlet_from_str(aumlet_str, 'VIT') + aumlet_from_str(aumlet_str, 'AAA')
        attr_data.t_mnd = t_vit_mnd - attr_data.t_vit
        return
    if 'double-angle-down' in icon_list[5]:
        # 全体魄
        attr_data.t_mnd = 1 + aumlet_from_str(aumlet_str, 'MND') + aumlet_from_str(aumlet_str, 'AAA')
        attr_data.t_vit = t_vit_mnd - attr_data.t_mnd
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

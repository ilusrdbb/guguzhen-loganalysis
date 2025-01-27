#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2023/6/6 10:02
# @Author : chaocai
import re

from core import config


class Attribute:
    # 初始化
    def __init__(self, enemy):
        if enemy:
            # 全部剩余点数
            self.all_point = int((6 + enemy.card_level * 3) * (100 + enemy.card_quality) / 100)
            # 总点数
            self.final_point = self.all_point
            # 总点数 包含苹果
            self.final_apple_point = 0
            # 力量
            self.t_str = 0
            # 敏捷
            self.t_agi = 0
            # 智力
            self.t_int = 0
            # 体魄
            self.t_vit = 0
            # 精神
            self.t_spr = 0
            # 意志
            self.t_mnd = 0
            # 双下-单下边界点
            self.point_down = 0
            # 单下-单上边界点
            self.point_up = 0
            # 单上-双上边界点
            self.point_double_up = 0


# 点数计算
def cal_attr(enemy_data, battle_data, attr_data, aumlet_str):
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
    # 根据护盾 推测精神
    cal_sld(enemy_data, battle_data, attr_data, aumlet_str)
    # 根据战斗记录 推测力量
    cal_battle_str(enemy_data, battle_data, attr_data, aumlet_str)
    # 根据血量 推测意志体魄
    cal_hp(enemy_data, battle_data, attr_data, aumlet_str)
    # 根据战斗记录 推测智力
    cal_battle_int(enemy_data, battle_data, attr_data, aumlet_str)
    # 剩余点数以及无法根据战斗记录推测时的处理
    cal_other_attr(battle_data, attr_data, aumlet_str)


# 战斗记录 魔伤推测智力
def cal_battle_int(enemy_data, battle_data, attr_data, aumlet_str):
    if attr_data.all_point == 0:
        return
    if enemy_data.enemy_card == 'YI' or enemy_data.enemy_card == 'XIA' or enemy_data.enemy_card == 'MING':
        return
    if enemy_data.enemy_card == 'MO' and battle_data.skl_flag:
        return
    m_damage = battle_data.m_damage
    if not m_damage:
        return
    attr_data.t_int = 1
    icon_list = battle_data.attr_list
    gear_list = battle_data.gear_list
    gear_level_list = battle_data.gear_level_list
    gear_mystery_list = battle_data.gear_mystery_list
    final_ratio = cal_final_ratio(enemy_data, battle_data)
    m_damage /= final_ratio
    # 斗篷转换
    if battle_data.is_cape:
        m_damage -= battle_data.cache_p_damage
    # 葡萄
    atk_aumlet_ratio = 1 + aumlet_from_str(aumlet_str, 'PATK') / 100
    atk_aumlet_ratio += int(int(config.read_config('wish_config').split(' ')[6]) / 100) / 100
    if enemy_data.enemy_card == 'WU':
        atk_aumlet_ratio += 0.3
    m_damage /= atk_aumlet_ratio
    # 后发
    if 'HOU' in battle_data.talent_list:
        m_damage /= (1 + 0.24 * battle_data.turn_num)
    # 手环神秘
    if battle_data.m_crt_flag:
        m_damage /= 2
    # 主动
    if battle_data.skl_flag:
        if enemy_data.enemy_card == 'WU':
            m_damage -= (100 - battle_data.wu_flag)
        if enemy_data.enemy_card == 'LIN':
            m_damage -= (battle_data.cache_p_atk * 2.2)
    # 暴击倍率
    crt_ratio = 1
    if battle_data.crt_flag:
        crt_ratio *= 2
        if enemy_data.enemy_card == 'MIN':
            crt_ratio *= 1.55
    # 面板后的加算
    pre_add = 0
    # 枪神秘
    if gear_list[0] == 'SPEAR' and gear_mystery_list[0] == '1':
        pre_add += (0.18 * battle_data.my_turn_hp)
    # 海星神秘
    if enemy_data.enemy_card == 'WU' and gear_list[1] == 'RING' and gear_mystery_list[1] == '1':
        pre_add += 0.2 * (battle_data.wu_flag + 100)
    # 梦
    if enemy_data.enemy_card == 'MENG':
        pre_add += (0.06 * battle_data.sld)
    # 计算基础魔攻
    if enemy_data.enemy_card == 'MENG' and battle_data.skl_flag:
        base_matk = (m_damage - crt_ratio * pre_add) / (crt_ratio + 2.25)
    else:
        base_matk = (m_damage - crt_ratio * pre_add) / crt_ratio
    # 黑夜雅
    if battle_data.my_card == 'YA':
        base_matk /= 0.7
    # 启程风
    if 'FENG' in battle_data.talent_list:
        base_matk -= 5 * (1 + int(config.read_config('wish_config').split(' ')[4]) * 0.05) * enemy_data.card_level
    # 装备 附加魔攻
    gear_add = 0
    if gear_list[1] == 'GLOVES':
        gear_add += int(gear_level_list[1]) * 10 * int(config.read_gear('gear_config')['GLOVES'].split(' ')[1]) / 100
    if gear_list[0] == 'STAFF':
        gear_add += int(gear_level_list[0]) * 10 * int(config.read_gear('gear_config')['STAFF'].split(' ')[1]) / 100
    base_matk -= gear_add
    # 许愿池
    base_matk -= int(config.read_config('wish_config').split(' ')[6]) * 5
    if base_matk <= 10:
        attr_data.all_point -= 1
        return
    # 装备 百分比魔攻
    gear_mul = 1
    if gear_list[0] == 'COLORFUL':
        gear_mul += (int(gear_level_list[0]) / 5 + 10) * int(config.read_gear('gear_config')['COLORFUL'].split(' ')[1]) / 10000
    if gear_list[0] == 'DAGGER':
        gear_mul += (int(gear_level_list[0]) / 5 + 10) * int(config.read_gear('gear_config')['DAGGER'].split(' ')[1]) / 10000
    if gear_list[1] == 'BRACELET':
        gear_mul += (int(gear_level_list[1]) / 5 + 1) * int(config.read_gear('gear_config')['BRACELET'].split(' ')[0]) / 10000
    if gear_list[0] == 'LIMPIDWAND':
        gear_mul += (int(gear_level_list[0]) / 5 + 20) * int(config.read_gear('gear_config')['LIMPIDWAND'].split(' ')[0]) / 10000
    if gear_list[0] == 'WAND':
        gear_mul += (int(gear_level_list[0]) / 5) * int(config.read_gear('gear_config')['WAND'].split(' ')[0]) / 10000
        gear_mul += (int(gear_level_list[0]) / 5) * int(config.read_gear('gear_config')['WAND'].split(' ')[1]) / 10000
        gear_mul += (int(gear_level_list[0]) / 5) * int(config.read_gear('gear_config')['WAND'].split(' ')[2]) / 10000
    # 加点，每点智力有多少魔攻
    kf_level = enemy_data.kf_level
    if kf_level >= 2000:
        kf_level = 2000
    t_int_mul = 10 + int(kf_level / 100) * 20
    # 反推
    attr_data.t_int = int(base_matk / gear_mul / t_int_mul)
    # 箭头校验
    attr_data.t_int = icon_check(attr_data.t_int, attr_data.final_apple_point, icon_list[2])
    # 点数正数校验
    if attr_data.t_int <= aumlet_from_str(aumlet_str, 'INT') + aumlet_from_str(aumlet_str, 'AAA'):
        attr_data.t_int = 1
        attr_data.all_point -= 1
        return
    attr_data.t_int -= (aumlet_from_str(aumlet_str, 'INT') + aumlet_from_str(aumlet_str, 'AAA'))
    # 点数溢出校验
    if attr_data.final_point <= attr_data.t_str + attr_data.t_spr + attr_data.t_int + attr_data.t_vit + attr_data.t_mnd + 1:
        attr_data.t_int = attr_data.final_point - attr_data.t_str - attr_data.t_spr - attr_data.t_vit - attr_data.t_mnd - 1
        attr_data.t_agi = 1
        attr_data.all_point = 0
        return
    attr_data.all_point -= attr_data.t_int


# 战斗记录 物伤推测力量
def cal_battle_str(enemy_data, battle_data, attr_data, aumlet_str):
    if attr_data.all_point == 0:
        return
    if enemy_data.enemy_card == 'YI' or enemy_data.enemy_card == 'XI' or enemy_data.enemy_card == 'YA':
        return
    p_damage = battle_data.p_damage
    if not p_damage:
        return
    attr_data.t_str = 1
    icon_list = battle_data.attr_list
    gear_list = battle_data.gear_list
    gear_level_list = battle_data.gear_level_list
    gear_mystery_list = battle_data.gear_mystery_list
    final_ratio = cal_final_ratio(enemy_data, battle_data)
    p_damage /= final_ratio
    # 斗篷转换
    if battle_data.is_cape:
        p_damage /= 2
        battle_data.cache_p_damage = p_damage
    # 葡萄
    atk_aumlet_ratio = 1 + aumlet_from_str(aumlet_str, 'PATK') / 100
    atk_aumlet_ratio += int(int(config.read_config('wish_config').split(' ')[6]) / 100) / 100
    if enemy_data.enemy_card == 'WU':
        atk_aumlet_ratio += 0.3
    p_damage /= atk_aumlet_ratio
    # 后发
    if 'HOU' in battle_data.talent_list:
        p_damage /= (1 + 0.24 * battle_data.turn_num)
    # 薇主动
    if enemy_data.enemy_card == 'WEI' and battle_data.skl_flag:
        p_damage /= 1.4
    # 薇被动
    if enemy_data.enemy_card == 'WEI' and gear_list[3] == 'HUNT' and gear_mystery_list[3] == '1':
        p_damage -= 0.147 * (battle_data.my_max_hp + battle_data.my_max_sld)
    elif enemy_data.enemy_card == 'WEI':
        p_damage -= 0.21 * (battle_data.my_max_hp + battle_data.my_max_sld)
    # 主动
    if battle_data.skl_flag:
        if enemy_data.enemy_card == 'WU':
            p_damage -= (100 - battle_data.wu_flag)
    # 琳底力
    di_damage = 0
    if battle_data.lin_flag:
        di_damage = battle_data.hp / 2
    # 暴击倍率
    crt_ratio = 1
    if battle_data.crt_flag:
        crt_ratio *= 2
        if enemy_data.enemy_card == 'MIN':
            crt_ratio *= 1.55
    # 面板后的加算
    pre_add = 0
    # 弓神秘
    if gear_list[0] == 'ASSBOW' and gear_mystery_list[0] == '1':
        pre_add += (0.18 * battle_data.my_turn_sld)
    # 沸血
    if 'FEI' in battle_data.talent_list:
        pre_add += (0.18 * battle_data.hp)
    # 海星神秘
    if enemy_data.enemy_card == 'WU' and gear_list[1] == 'RING' and gear_mystery_list[1] == '1':
        pre_add += 0.2 * (battle_data.wu_flag + 100)
    # 计算基础物攻
    if enemy_data.enemy_card == 'LIN' and battle_data.skl_flag:
        base_patk = (p_damage - di_damage - crt_ratio * pre_add) / (crt_ratio + 2.2)
    else:
        base_patk = (p_damage - di_damage - crt_ratio * pre_add) / crt_ratio
    battle_data.cache_p_atk = base_patk
    # 黑夜雅
    if battle_data.my_card == 'YA':
        base_patk /= 0.7
    # 启程风
    if 'FENG' in battle_data.talent_list:
        base_patk -= 5 * (1 + int(config.read_config('wish_config').split(' ')[4]) * 0.05) * enemy_data.card_level
    # 装备 附加物攻
    gear_add = 0
    if gear_list[1] == 'GLOVES':
        gear_add += int(gear_level_list[1]) * 10 * int(config.read_gear('gear_config')['GLOVES'].split(' ')[0]) / 100
    if gear_list[0] == 'CLAYMORE':
        gear_add += int(gear_level_list[0]) * 20 * int(config.read_gear('gear_config')['CLAYMORE'].split(' ')[0]) / 100
        gear_add += int(gear_level_list[0]) * 20 * int(config.read_gear('gear_config')['CLAYMORE'].split(' ')[1]) / 100
    if gear_list[0] == 'STAFF':
        gear_add += int(gear_level_list[0]) * 10 * int(config.read_gear('gear_config')['STAFF'].split(' ')[0]) / 100
    base_patk -= gear_add
    # 许愿池
    base_patk -= int(config.read_config('wish_config').split(' ')[6]) * 5
    if base_patk <= 10:
        attr_data.all_point -= 1
        return
    # 装备 百分比物攻
    gear_mul = 1
    if gear_list[0] == 'COLORFUL':
        gear_mul += (int(gear_level_list[0]) / 5 + 10) * int(config.read_gear('gear_config')['COLORFUL'].split(' ')[0]) / 10000
    if gear_list[0] == 'SPEAR':
        gear_mul += (int(gear_level_list[0]) / 5 + 50) * int(config.read_gear('gear_config')['SPEAR'].split(' ')[0]) / 10000
    if gear_list[0] == 'CLAYMORE':
        gear_mul += (int(gear_level_list[0]) / 5 + 30) * int(config.read_gear('gear_config')['CLAYMORE'].split(' ')[2]) / 10000
    if gear_list[0] == 'DAGGER':
        gear_mul += (int(gear_level_list[0]) / 5 + 10) * int(config.read_gear('gear_config')['DAGGER'].split(' ')[0]) / 10000
    if gear_list[0] == 'ASSBOW':
        gear_mul += (int(gear_level_list[0]) / 5 + 30) * int(config.read_gear('gear_config')['ASSBOW'].split(' ')[0]) / 10000
    if gear_list[0] == 'BLADE':
        gear_mul += (int(gear_level_list[0]) / 5 + 20) * int(config.read_gear('gear_config')['BLADE'].split(' ')[0]) / 10000
    # 加点，每点力量有多少物攻
    kf_level = enemy_data.kf_level
    if kf_level >= 2000:
        kf_level = 2000
    t_str_mul = 10 + int(kf_level / 100) * 20
    # 反推
    attr_data.t_str = int(base_patk / gear_mul / t_str_mul)
    # 箭头校验
    attr_data.t_str = icon_check(attr_data.t_str, attr_data.final_apple_point, icon_list[0])
    # 点数正数校验
    if attr_data.t_str <= aumlet_from_str(aumlet_str, 'STR') + aumlet_from_str(aumlet_str, 'AAA'):
        attr_data.t_str = 1
        attr_data.all_point -= 1
        return
    attr_data.t_str -= (aumlet_from_str(aumlet_str, 'STR') + aumlet_from_str(aumlet_str, 'AAA'))
    # 点数溢出校验
    if attr_data.final_point <= attr_data.t_str + attr_data.t_spr + 4:
        attr_data.t_str = attr_data.final_point - attr_data.t_spr - 4
        attr_data.t_int = 1
        attr_data.t_agi = 1
        attr_data.t_vit = 1
        attr_data.t_mnd = 1
        attr_data.all_point = 0
        return
    attr_data.all_point -= attr_data.t_str


# 分析战斗记录获取最终乘算倍率
def cal_final_ratio(enemy_data, battle_data):
    final_ratio = 1
    # 进攻防御等级
    final_ratio *= get_level_ratio(enemy_data, 'attack')
    final_ratio *= get_level_ratio(enemy_data, 'defense')
    # 抵抗
    if battle_data.skl_flag:
        final_ratio *= 1 - config.read_config('skl_def') / 100
    if battle_data.crt_flag:
        final_ratio *= 1 - config.read_config('crt_def') / 100
    # 光环影响
    if 'ZI' in battle_data.talent_list:
        final_ratio *= 1.5
    if 'DIAN' in battle_data.talent_list:
        final_ratio *= 0.7
    if 'ZOU' in battle_data.talent_list or 'ZOU' in battle_data.my_talent_list:
        zou_ratio = 0.3 + battle_data.turn_num * 0.2
        if zou_ratio > 10:
            zou_ratio = 10
        final_ratio *= zou_ratio
    if 'PEN' in battle_data.talent_list or 'PEN' in battle_data.my_talent_list:
        if battle_data.crt_flag:
            final_ratio *= 1.4
        else:
            final_ratio *= 0.6
    return final_ratio


# 获取进攻防御等级带来的伤害倍率
def get_level_ratio(enemy_data, level_type):
    enemy_kf_level = enemy_data.kf_level
    if enemy_kf_level >= 2000:
        enemy_kf_level = 2000
    my_kf_level = enemy_data.my_kf_level
    if my_kf_level >= 2000:
        my_kf_level = 2000
    if config.read_config('rank_level') > 0:
        enemy_kf_level += config.read_config('rank_level') * 100
    if config.read_config('rank_level') < 0:
        my_kf_level += config.read_config('rank_level') * 100
    if enemy_kf_level > my_kf_level and level_type == 'attack':
        return 1 + 0.03 * int((enemy_kf_level - my_kf_level) / 100)
    if my_kf_level > enemy_kf_level and level_type == 'defense':
        return 1 - 0.03 * int((my_kf_level - enemy_kf_level) / 100)
    return 1


# 根据剩余点数和图标大致推断力量、智力、敏捷
def cal_other_attr(battle_data, attr_data, aumlet_str):
    if attr_data.all_point == 0:
        return
    if attr_data.t_str > 0 and attr_data.t_int > 0:
        attr_data.t_agi = attr_data.all_point
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
            if attr_data.t_str > 0:
                attr_data.t_agi = attr_data.all_point - 1
                attr_data.t_int = 1
                return
            elif attr_data.t_int > 0:
                attr_data.t_agi = attr_data.all_point - 1
                attr_data.t_str = 1
                return
            else:
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
    if attr_data.t_str > 0:
        if t_agi >= attr_data.all_point - 1:
            attr_data.t_agi = attr_data.all_point - 1
            attr_data.t_int = 1
            return
        attr_data.t_agi = t_agi
        attr_data.all_point -= t_agi
        attr_data.t_int = attr_data.all_point
    elif attr_data.t_int > 0:
        if t_agi >= attr_data.all_point - 1:
            attr_data.t_agi = attr_data.all_point - 1
            attr_data.t_str = 1
            return
        attr_data.t_agi = t_agi
        attr_data.all_point -= t_agi
        attr_data.t_str = attr_data.all_point
    else:
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


# 护盾计算
def cal_sld(enemy_data, battle_data, attr_data, aumlet_str):
    icon_list = battle_data.attr_list
    gear_list = battle_data.gear_list
    gear_level_list = battle_data.gear_level_list
    gear_mystery_list = battle_data.gear_mystery_list
    sld = battle_data.sld
    # 加点，每点精神有多少护盾
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
        gear_add += int(gear_level_list[1]) * 20 * int(config.read_gear('gear_config')['BRACELET'].split(' ')[2]) / 100
    if gear_list[2] == 'CLOAK':
        gear_add += int(gear_level_list[2]) * 50 * int(config.read_gear('gear_config')['CLOAK'].split(' ')[3]) / 100
    if gear_list[2] == 'CAPE':
        gear_add += int(gear_level_list[2]) * 100 * int(config.read_gear('gear_config')['CAPE'].split(' ')[1]) / 100
    if gear_list[3] == 'TIARA':
        gear_add += int(gear_level_list[3]) * 20 * int(config.read_gear('gear_config')['TIARA'].split(' ')[2]) / 100
    # 装备 百分比护盾
    gear_mul = 1
    if gear_list[2] == 'CLOAK':
        gear_mul += (int(gear_level_list[2]) / 5 + 25) * int(config.read_gear('gear_config')['CLOAK'].split(' ')[2]) / 10000
    if gear_list[2] == 'CAPE':
        gear_mul += (int(gear_level_list[2]) / 5 + 50) * int(config.read_gear('gear_config')['CAPE'].split(' ')[0]) / 10000
    if gear_list[3] == 'TIARA':
        gear_mul += int(gear_level_list[3]) / 5 * int(config.read_gear('gear_config')['TIARA'].split(' ')[1]) / 10000
    # 最后乘算因素
    final_ratio = 1
    final_ratio += aumlet_from_str(aumlet_str, 'SLD') / 100
    final_ratio += int(int(config.read_config('wish_config').split(' ')[8]) / 100) / 100
    if gear_list[2] == 'CLOAK' and gear_mystery_list[2] == '1':
        final_ratio += 0.5
    if enemy_data.enemy_card == 'MO':
        final_ratio += 0.25
    if enemy_data.enemy_card == 'MENG':
        if gear_list[3] == 'TIARA' and gear_mystery_list[3] == '1':
            final_ratio += 0.45
        else:
            final_ratio += 0.3
    if enemy_data.enemy_card == 'WU':
        final_ratio += 0.3
    if enemy_data.enemy_card == 'XIA':
        final_ratio += 0.01 * int(config.read_config('default_g') / 5000)
    # 反推
    base_sld = (sld / final_ratio - gear_add - wish_add - xin_add) / gear_mul
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
        gear_add += int(gear_level_list[1]) * 10 * int(config.read_gear('gear_config')['GLOVES'].split(' ')[3]) / 100
    # 根据箭头大致加点
    t_str = get_about_point(icon_list[0], attr_data.final_apple_point, 'str', attr_data.t_str)
    t_agi = get_about_point(icon_list[1], attr_data.final_apple_point, 'agi', None)
    t_vit = get_about_point(icon_list[3], attr_data.final_apple_point, 'vit', None)
    t_mnd = get_about_point(icon_list[5], attr_data.final_apple_point, 'mnd', None)
    if gear_list[1] == 'DEVOUR':
        gear_add += t_str * int(gear_level_list[1]) * 0.08 * int(config.read_gear('gear_config')['DEVOUR'].split(' ')[2]) / 100
    if gear_list[1] == 'REFRACT':
        gear_add += t_agi * int(gear_level_list[1]) * 0.05 * int(config.read_gear('gear_config')['REFRACT'].split(' ')[3]) / 100
    if gear_list[2] == 'CLOAK':
        gear_add += int(gear_level_list[2]) * 10 * int(config.read_gear('gear_config')['CLOAK'].split(' ')[0]) / 100
    if gear_list[3] == 'SCARF':
        gear_add += int(gear_level_list[3]) * 10 * int(config.read_gear('gear_config')['SCARF'].split(' ')[0]) / 100
    if gear_list[3] == 'TIARA':
        gear_add += int(gear_level_list[3]) * 5 * int(config.read_gear('gear_config')['TIARA'].split(' ')[0]) / 100
    if gear_list[3] == 'RIBBON':
        gear_add += t_vit * int(gear_level_list[3]) / 30 * int(config.read_gear('gear_config')['RIBBON'].split(' ')[2]) / 100
        gear_add += t_mnd * int(gear_level_list[3]) / 30 * int(config.read_gear('gear_config')['RIBBON'].split(' ')[3]) / 100
    if gear_list[3] == 'HUNT':
        gear_add += t_str * int(gear_level_list[3]) * 0.08 * int(config.read_gear('gear_config')['HUNT'].split(' ')[1]) / 100
        gear_add += t_agi * int(gear_level_list[3]) * 0.08 * int(config.read_gear('gear_config')['HUNT'].split(' ')[2]) / 100
    # 装备 百分比生命
    gear_mul = 1
    if gear_list[1] == 'DEVOUR':
        gear_mul += int(gear_level_list[1]) * 0.07 * int(config.read_gear('gear_config')['DEVOUR'].split(' ')[3]) / 10000
    if gear_list[2] == 'THORN':
        gear_mul += (int(gear_level_list[2]) / 5 + 20) * int(config.read_gear('gear_config')['THORN'].split(' ')[0]) / 10000
    if gear_list[2] == 'WOOD':
        gear_mul += (int(gear_level_list[2]) / 5 + 50) * int(config.read_gear('gear_config')['WOOD'].split(' ')[0]) / 10000
    if gear_list[3] == 'HUNT':
        gear_mul += int(gear_level_list[3]) * 0.06 * int(config.read_gear('gear_config')['HUNT'].split(' ')[3]) / 10000
    # 最后乘算因素
    final_ratio = 1
    final_ratio += aumlet_from_str(aumlet_str, 'HP') / 100
    final_ratio += int(int(config.read_config('wish_config').split(' ')[7]) / 100) / 100
    if enemy_data.enemy_card == 'LIN':
        final_ratio += 0.3
    if enemy_data.enemy_card == 'YI':
        final_ratio += 0.2
    if enemy_data.enemy_card == 'XI':
        final_ratio += 0.01 * int(config.read_config('default_g') / 2000)
    if enemy_data.enemy_card == 'MING':
        final_ratio += 0.9
    if enemy_data.enemy_card == 'WU':
        final_ratio += 0.3
    # 反推
    base_hp = (hp / final_ratio - gear_add - wish_add - xin_add) / gear_mul
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


# 根据箭头大致加点，用于推测例如猎魔头这种根据点数加血的装备
def get_about_point(icon_str, final_apple_point, attr_type, pre_cal_str):
    if attr_type == 'str' and pre_cal_str > 0:
        return pre_cal_str
    if attr_type != 'agi':
        if 'double-angle-up' in icon_str:
            return int(final_apple_point * 0.5)
        if 'icon-angle-up' in icon_str:
            return int(final_apple_point * 0.3)
        if 'icon-angle-down' in icon_str:
            return int(final_apple_point * 0.15)
        if 'double-angle-down' in icon_str:
            return 1
    else:
        if 'double-angle-up' in icon_str:
            return int(final_apple_point * 0.7)
        if 'icon-angle-up' in icon_str:
            return int(final_apple_point * 0.35)
        if 'icon-angle-down' in icon_str:
            return int(final_apple_point * 0.15)
        if 'double-angle-down' in icon_str:
            return 1
    return 1

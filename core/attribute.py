#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2023/1/4 9:50
# @Author : chaocai
import re

from lxml import html

from config import *
from core import gear


def get_attribute_map(battle_log_str, talent_list, enemy_level):
    # 解析html
    battle_log_dom = html.fromstring(battle_log_str)
    # 获取装备list
    gear_list = gear.get_gear_list(battle_log_dom)
    # 获取装备等级list
    level_list = gear.get_level_list(battle_log_dom)
    # 获取装备属性list
    _gear_list = gear.get_gear_map_list(gear_list, level_list)
    # 获取全部属性的字符串
    attribute_str = ''.join(battle_log_dom.xpath(XPATH_CONFIG['DATA']))
    # 获取属性 生命
    attribute_hp = get_hp(attribute_str)
    # 获取属性 护盾
    attribute_sld = get_sld(attribute_str)
    # 获取属性 速度
    attribute_spd = get_spd(attribute_str)
    # 获取属性 物防
    attribute_pdef = get_pdef(attribute_str, talent_list)
    # 获取属性 魔防
    attribute_mdef = get_mdef(attribute_str, talent_list)
    # 获取属性 物攻
    attribute_patk = get_patk(attribute_str)
    # 获取属性 魔攻
    attribute_matk = get_matk(attribute_str)
    # 获取属性 物穿
    attribute_pth = get_pth(_gear_list, talent_list)
    # 获取属性 魔穿
    attribute_mth = get_mth(_gear_list, talent_list)
    # 获取属性 暴穿
    attribute_cth = get_cth(_gear_list)
    # 推测加点 力量
    cal_str = get_str(attribute_patk, talent_list, _gear_list, enemy_level)
    # 推测加点 智力
    cal_int = get_int(attribute_matk, talent_list, _gear_list, enemy_level)
    # 推测加点 敏捷
    cal_agi = get_agi(attribute_spd, _gear_list)
    # 获取属性 附加物穿
    _attribute_pth = _get_pth(_gear_list, talent_list, attribute_pth, cal_str, enemy_level)
    # 获取属性 附加魔穿
    _attribute_mth = _get_mth(_gear_list, talent_list, attribute_mth, cal_int, enemy_level)
    # 获取属性 物理减伤
    attribute_pdec = get_pdec(_gear_list, talent_list, enemy_level)
    # 获取属性 魔法减伤
    attribute_mdec = get_mdec(_gear_list, talent_list, enemy_level)
    # 获取属性 回血比例
    attribute_hpr = get_hpr(cal_str)
    # 获取属性 回盾比例
    attribute_sldr = get_sldr(cal_int, _gear_list)
    # 获取属性 附加回血
    _attribute_hpr = _get_hpr(_gear_list)
    # 获取属性 附加回盾
    _attribute_sldr = _get_sldr(_gear_list)
    # 获取属性 暴击
    attribute_crt = get_crt(_gear_list, cal_agi)
    # 获取属性 技能
    attribute_skl = get_skl(_gear_list, cal_int)
    # 获取属性 反弹
    attribute_rfl = get_rfl(_gear_list, talent_list)
    # 获取属性 吸血
    attribute_lch = get_lch(_gear_list, talent_list)
    return {
        'hp': attribute_hp,
        'sld': attribute_sld,
        'spd': get_final_spd(attribute_spd),
        'pdef': attribute_pdef,
        'mdef': attribute_mdef,
        'patk': attribute_patk,
        'matk': attribute_matk,
        'pth': attribute_pth,
        'mth': attribute_mth,
        'cth': attribute_cth,
        '_pth': _attribute_pth,
        '_mth': _attribute_mth,
        'pdec': attribute_pdec,
        'mdec': attribute_mdec,
        'hpr': attribute_hpr,
        'sldr': attribute_sldr,
        '_hpr': _attribute_hpr,
        '_sldr': _attribute_sldr,
        'crt': attribute_crt,
        'skl': attribute_skl,
        'rfl': attribute_rfl,
        'lch': attribute_lch,
        'gear': gear_list,
    }


# 获取属性 吸血
def get_lch(_gear_list, talent_list):
    lch = gear.get_sum_point(_gear_list, 'LCH')
    if 'XUE' in talent_list:
        lch = lch + XUE_ADD_LCH
    return lch


# 获取属性 反伤
def get_rfl(_gear_list, talent_list):
    rfl = gear.get_sum_point(_gear_list, 'RFL')
    if 'CI' in talent_list:
        rfl = rfl + CI_ADD_RFL
    return rfl


# 获取属性 技能
def get_skl(_gear_list, cal_int):
    skl = gear.get_sum_point(_gear_list, '_SKL')
    skl = skl + cal_int * INT_MU_SKL
    return skl


# 获取属性 暴击
def get_crt(_gear_list, cal_agi):
    crt = gear.get_sum_point(_gear_list, '_CRT')
    crt = crt + cal_agi * AGI_MU_CRT
    return crt


# 获取属性 附加回盾
def _get_sldr(_gear_list):
    return gear.get_sum_point(_gear_list, '_SLDR')


# 获取属性 附加回血
def _get_hpr(_gear_list):
    return gear.get_sum_point(_gear_list, '_HPR')


# 获取属性 回盾比例
def get_sldr(cal_int, _gear_list):
    sldr = int(cal_int / INT_DIV_SLDR)
    sldr = sldr + gear.get_sum_point(_gear_list, 'SLDR')
    return sldr


# 获取属性 回血比例
def get_hpr(cal_str):
    return int(cal_str / STR_DIV_HPR)


# 获取属性 魔法减伤
def get_mdec(_gear_list, talent_list, enemy_level):
    mdec = gear.get_sum_point(_gear_list, '_MDEC')
    if 'SHI' in talent_list:
        mdec = mdec + enemy_level * SHI_MU_DEC
    return mdec


# 获取属性 物理减伤
def get_pdec(_gear_list, talent_list, enemy_level):
    pdec = gear.get_sum_point(_gear_list, '_PDEC')
    if 'SHI' in talent_list:
        pdec = pdec + enemy_level * SHI_MU_DEC
    return pdec


# 获取属性 附加魔穿
def _get_mth(_gear_list, talent_list, attribute_mth, cal_int, enemy_level):
    _mth = gear.get_sum_point(_gear_list, '_MTH')
    _mth = int(_mth + cal_int * INT_MU_MTH)
    if 'MO' in talent_list:
        _mth = int(_mth * BI_MU_TH)
    if 'HONG' in talent_list and attribute_mth > HONG_TH_LIMIT:
        _mth = int(_mth + (enemy_level / HONG_DIV_TH))
    if 'TIAO' in talent_list and enemy_level < MY_LEVEL:
        _mth = _mth + (MY_LEVEL - enemy_level) * 2
    return _mth


# 获取属性 附加物穿
def _get_pth(_gear_list, talent_list, attribute_pth, cal_str, enemy_level):
    _pth = gear.get_sum_point(_gear_list, '_PTH')
    _pth = _pth + cal_str * STR_MU_PTH
    if 'BI' in talent_list:
        _pth = int(_pth * MO_MU_TH)
    if 'HONG' in talent_list and attribute_pth > HONG_TH_LIMIT:
        _pth = int(_pth + (enemy_level / HONG_DIV_TH))
    if 'TIAO' in talent_list and enemy_level < MY_LEVEL:
        _pth = _pth + (MY_LEVEL - enemy_level) * 2
    return _pth


# 推测加点 敏捷
def get_agi(attribute_spd, _gear_list):
    spd = gear.get_sum_point(_gear_list, 'SPD')
    _spd = gear.get_sum_point(_gear_list, '_SPD')
    attribute_spd = attribute_spd - _spd
    if attribute_spd < 0:
        attribute_spd = 0
    return int(attribute_spd / ((spd + 100) / 100) / AGI_MU_SPD)


# 推测加点 力量
def get_str(attribute_patk, talent_list, _gear_list, enemy_level):
    patk = gear.get_sum_point(_gear_list, 'PATK')
    _patk = gear.get_sum_point(_gear_list, '_PATK')
    attribute_patk = attribute_patk - _patk
    if 'FENG' in talent_list:
        attribute_patk = attribute_patk - enemy_level * FENG_MU_ATK
    if attribute_patk < 0:
        attribute_patk = 0
    return int(attribute_patk / ((patk + 100) / 100) / STR_MU_PATK)


# 推测加点 智力
def get_int(attribute_matk, talent_list, _gear_list, enemy_level):
    matk = gear.get_sum_point(_gear_list, 'MATK')
    _matk = gear.get_sum_point(_gear_list, '_MATK')
    attribute_matk = attribute_matk - _matk
    if 'FENG' in talent_list:
        attribute_matk = attribute_matk - enemy_level * FENG_MU_ATK
    if attribute_matk < 0:
        attribute_matk = 0
    return int(attribute_matk / ((matk + 100) / 100) / INT_MU_MATK)


# 获取属性 暴穿
def get_cth(_gear_list):
    return gear.get_sum_point(_gear_list, 'CTH')


# 获取属性 物穿
def get_pth(_gear_list, talent_list):
    pth = gear.get_sum_point(_gear_list, 'PTH')
    if 'BI' in talent_list:
        pth = int(pth * BI_MU_TH)
    if 'HONG' in talent_list and pth < HONG_TH_LIMIT:
        pth = HONG_TH_LIMIT
    return pth


# 获取属性 魔穿
def get_mth(_gear_list, talent_list):
    mth = gear.get_sum_point(_gear_list, 'MTH')
    if 'MO' in talent_list:
        mth = int(mth * MO_MU_TH)
    if 'HONG' in talent_list and mth < HONG_TH_LIMIT:
        mth = HONG_TH_LIMIT
    return mth


# 获取属性 魔防
def get_mdef(attribute_str, talent_list):
    mdef = int(re.findall(MATCH_CONFIG['MDEF'], attribute_str)[0])
    if 'DIAN' in talent_list:
        mdef = int(mdef * DIAN_MU_DEF)
    return mdef


# 获取属性 物防
def get_pdef(attribute_str, talent_list):
    pdef = int(re.findall(MATCH_CONFIG['PDEF'], attribute_str)[0])
    if 'DIAN' in talent_list:
        pdef = int(pdef * DIAN_MU_DEF)
    return pdef


# 获取属性 物攻
def get_patk(attribute_str):
    return int(re.findall(MATCH_CONFIG['PATK'], attribute_str)[0])


# 获取属性 魔攻
def get_matk(attribute_str):
    return int(re.findall(MATCH_CONFIG['MATK'], attribute_str)[0])


# 获取属性 生命
def get_hp(attribute_str):
    return int(re.findall(MATCH_CONFIG['HP'], attribute_str)[0])


# 获取属性 护盾
def get_sld(attribute_str):
    return int(re.findall(MATCH_CONFIG['SLD'], attribute_str)[0])


# 获取属性 速度
def get_spd(attribute_str):
    return int(re.findall(MATCH_CONFIG['SPD'], attribute_str)[0])


# 获取属性 最终速度
def get_final_spd(spd):
    if spd > SPEED_ADD:
        spd = int(spd * SPD_MU_MAX)
    return spd

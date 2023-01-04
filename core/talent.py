#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2023/1/4 9:50
# @Author : chaocai
import re

from lxml import html

from config import *


def get_talent_list(battle_log_str):
    # 解析html
    battle_log_dom = html.fromstring(battle_log_str)
    talent_str = ''.join(battle_log_dom.xpath(XPATH_CONFIG['TALENT']))
    # 获取天赋list
    return _get_talent_list(talent_str)


# 获取天赋list
def _get_talent_list(talent_str):
    result_list = []
    talent_list = re.findall(MATCH_CONFIG['TALENT'], talent_str)
    for talent in talent_list:
        talent = talent.replace('|', '').replace('<br>', '')
        if talent:
            result_list.append(TALENT_MAP[talent])
    return result_list

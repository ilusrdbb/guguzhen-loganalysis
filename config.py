#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2022/12/16 14:16
# @Author : chaocai

# 黑名单，不记录这个人，优先级最高
BLACK_LIST = []

# 最低等级，小于这个等级的跳过不记录
MIN_LEVEL = 750

# 自身等级，用于计算等级压制/等级挑战
MY_LEVEL = 850

# 在此日期前的跳过不记录，如果为空则全量抓取，因为3s环境变化较快不建议设置太久远
LAST_DATE = '2022-12-23'

# 默认护符
DEFAULT_AMULET = 'REC 10 SKL 10 CRT 10 PDEF 10 MDEF 10'

# 速度阈值，大于此速度的卷逼最终速度再乘1.1的速度葡萄
SPEED_ADD = 5000

# 默认许愿池
DEFAULT_WISH = '5 5 5 5 5 5 5'

# 默认携带神秘的装备
DEFULT_SECRET = ['ASSBOW', 'DAGGER', 'WAND', 'SHIELD', 'CLAYMORE', 'SPEAR', 'VULTURE',
                 'WOOD', 'CAPE', 'TIARA', 'RIBBON', 'RING', 'DEVOUR']

# 装备默认属性，觉得欧狗多就设置的高些，注意设置的太高胜率容易尿崩
# 带_的属性为加算的附加数值，不带的为乘算比值 TH 穿透 DEC 减伤 R 回复
DEFAULT_GEAR = {
    'STAFF': {'_PATK': 4000, '_MATK': 4000, 'MTH': 29, 'LCH': 30},
    'BLADE': {'PATK': 80, 'PTH': 36, 'CTH': 36, 'SPD': 115},
    'ASSBOW': {'PATK': 100, 'PTH': 36, 'CTH': 36, '_PTH': 300},
    'DAGGER': {'PATK': 75, 'MATK': 75, '_SPD': 1500, 'SPD': 120},
    'WAND': {'MATK': 210, 'PTH': 21},
    'SHIELD': {'LCH': 30, 'RFL': 38},  # 默认加反伤樱桃的10反
    'CLAYMORE': {'_PATK': 10000, 'PATK': 110, 'CTH': 22},
    'SPEAR': {'PATK': 110, 'PTH': 30, '_MTH': 850, 'LCH': 30},
    'GLOVES': {'_PATK': 4000, '_MATK': 4000, '_SPD': 850},
    'BRACELET': {'MATK': 85, 'MTH': 23},
    'VULTURE': {'LCH': 80, '_SPD': 800},
    'CLOAK': {'_SLDR': 20000},
    'THORN': {'RFL': 70},  # 默认带神秘
    'WOOD': {'_HPR': 8000, '_PDEC': 1500, '_MDEC': 1500},
    'CAPE': {'_MDEC': 2000},
    'SCARF': {'_PDEC': 800, '_MDEC': 800, '_HPR': 1500},
    'TIARA': {'_PDEC': 800},
    'RIBBON': {'_HPR': 1500, 'SLDR': 12},
    'RING': {'_PTH': 200, '_MTH': 200, '_CRT': 300, '_SKL': 300},
    'DEVOUR': {'_MTH': 200, '_SKL': 300},
}

# 默认成长值，目前只影响舞
DEFAULT_G = 50000

# 下面的设置最好不要乱动，除非你对游戏以及源码有足够的了解
# 卡片映射
CARD_MAP = {
    '默': 'MO',
    '琳': 'LIN',
    '艾': 'AI',
    '梦': 'MENG',
    '薇': 'WEI',
    '冥': 'MING',
    '命': 'MIN',
    '伊': 'YI',
    '希': 'XI',
    '舞': 'WU',
}

# 装备映射
GEAR_MAP = {
    '探险者短杖': 'STAFF',
    '狂信者的荣誉之刃': 'BLADE',
    '反叛者的刺杀弓': 'ASSBOW',
    '幽梦匕首': 'DAGGER',
    '光辉法杖': 'WAND',
    '荆棘剑盾': 'SHIELD',
    '陨铁重剑': 'CLAYMORE',
    '饮血长枪': 'SPEAR',
    '探险者手套': 'GLOVES',
    '命师的传承手环': 'BRACELET',
    '秃鹫手套': 'VULTURE',
    '旅法师的灵光袍': 'CLOAK',
    '战线支撑者的荆棘重甲': 'THORN',
    '复苏木甲': 'WOOD',
    '挑战斗篷': 'CAPE',
    '探险者头巾': 'SCARF',
    '占星师的发饰': 'TIARA',
    '天使缎带': 'RIBBON',
    '海星戒指': 'RING',
    '噬魔戒指': 'DEVOUR',
}

# 需要在生成的配置里填写的天赋
TALENT_CONFIG = ['DUN', 'XUE', 'XIAO', 'SHENG', 'E', 'SHANG', 'SHEN', 'REN'
    , 'RE', 'DIAN', 'WU', 'ZHI', 'FEI', 'BO', 'JU', 'JUE', 'HOU', 'DUNH', 'ZI']

# 天赋映射
TALENT_MAP = {
    '启程之誓': 'SHI',
    '启程之心': 'XIN',
    '启程之风': 'FENG',
    '等级挑战': 'TIAO',
    '等级压制': 'YA',
    '破壁之心': 'BI',
    '破魔之心': 'MO',
    '复合护盾': 'DUN',
    '鲜血渴望': 'XUE',
    '削骨之痛': 'XIAO',
    '圣盾祝福': 'SHENG',
    '恶意抽奖': 'E',
    '伤口恶化': 'SHANG',
    '精神创伤': 'SHEN',
    '铁甲尖刺': 'CI',
    '忍无可忍': 'REN',
    '热血战魂': 'RE',
    '点到为止': 'DIAN',
    '午时已到': 'WU',
    '纸薄命硬': 'ZHI',
    '沸血之志': 'FEI',
    '波澜不惊': 'BO',
    '飓风之力': 'JU',
    '红蓝双刺': 'HONG',
    '荧光护盾': 'JUE',
    '后发制人': 'HOU',
    '钝化锋芒': 'DUNH',
    '自信回头': 'ZI',
}

# xpath设置
XPATH_CONFIG = {
    'DATA': '//div[contains(@class,\'alert-info\')]/div//div[contains(@class,\'fyg_tl\')]//text()',
    'TALENT': '//div[contains(@class,\'alert-info\')]/div//div[contains(@class,\'fyg_tr\')]//text()',
    'GEAR': '//button[contains(@class,\'fyg_colpzbg\')]/@data-original-title',
}

# 正则设置
MATCH_CONFIG = {
    'HP': '(?<=\\[生命:).*?(?=\\])',
    'SLD': '(?<=\\[护盾:).*?(?=\\])',
    'SPD': '(?<=\\[速度:).*?(?=\\])',
    'PATK': '(?<=\\[物攻:).*?(?=\\])',
    'MATK': '(?<=\\[魔攻:).*?(?=\\])',
    'PDEF': '(?<=\\[物防:).*?(?=\\])',
    'MDEF': '(?<=\\[魔防:).*?(?=\\])',
    'TALENT': '(?<=\\|).*?(?=\\|)',
}

# 输入文件路径
INPUT_PATH = './source/1.txt'

# 输出文件路径
OUTPUT_PATH = './source/pc.txt'

# 一些游戏的基础属性
# 鲜血渴望 吸血
XUE_ADD_LCH = 10
# 铁甲尖刺 反伤
CI_ADD_RFL = 20
# 智力 技能倍率
INT_MU_SKL = 1
# 敏捷 暴击倍率
AGI_MU_CRT = 1
# 智力 回盾倍率
INT_DIV_SLDR = 200
# 力量 回血倍率
STR_DIV_HPR = 120
# 启程之誓 减伤等级倍率
SHI_MU_DEC = 2
# 启程之风 附加攻击倍率
FENG_MU_ATK = 5
# 力量 附加物穿倍率
STR_MU_PTH = 1
# 智力 附加魔穿倍率
INT_MU_MTH = 1.1
# 红蓝 穿透判定阈值
HONG_TH_LIMIT = 40
# 红蓝 附加穿透 倍率
HONG_DIV_TH = 2
# 破壁 穿透倍率
BI_MU_TH = 1.15
# 破魔 穿透倍率
MO_MU_TH = 1.15
# 敏捷 速度倍率
AGI_MU_SPD = 3
# 力量 物攻倍率
STR_MU_PATK = 10
# 智力 魔攻倍率
INT_MU_MATK = 12
# 点到 防御倍率
DIAN_MU_DEF = 1.3
# 速度葡萄上限
SPD_MU_MAX = 1.1

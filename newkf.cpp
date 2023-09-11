#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>
#include <sys/time.h>
#include <stdint.h>
#include <pthread.h>
#include <unistd.h>
#include <signal.h>
#include <string>
#include <vector>
#include <queue>
#include <tr1/unordered_map>
#include <tr1/unordered_set>

uint64_t crc64r(const void* ptr, size_t size, uint64_t crc = 0xFFFFFFFFFFFFFFFFULL)
{
    static uint64_t sCrcTable[256];
    static bool init = false;

    if (!init)
    {
        for (int i = 0; i < 256; ++i)
        {
            uint64_t n = i;
            for (int j = 0; j < 8; ++j)
            {
                n = (n >> 1) ^ (n & 1 ? 0x95AC9329AC4BC9B5ULL : 0ULL);
            }
            sCrcTable[i] = n;
        }
        init = true;
    }

    const unsigned char* buffer = reinterpret_cast<const unsigned char*>(ptr);
    for (size_t i = 0; i < size; ++i)
    {
        crc = sCrcTable[(crc ^ buffer[i]) & 0xFFU] ^ (crc >> 8);
    }
    return crc;
}

enum
{
    ROLE_NPC = 0,
    ROLE_MU = 0, // 铁皮木人
    ROLE_ZHU,    // 嗜血的迅捷蛛
    ROLE_DENG,   // 魔灯之灵
    ROLE_SHOU,   // 戆戆的食铁兽
    ROLE_MU2,    // 铁皮木人(新版)
    ROLE_ZHU2,   // 迅捷魔蛛(新版)
    ROLE_DENG2,  // 魔灯之灵(新版)
    ROLE_SHOU2,  // 食铁兽(新版)
    ROLE_YU2,    // 六眼飞鱼(新版)
    ROLE_HAO2,   // 晶刺豪猪(新版)
    ROLE_LIU,    // 六边形战士
    ROLE_SHI,    // 史莱姆
    NPC_COUNT_OLD = 4,
    NPC_COUNT_OLD2 = 10,
    NPC_COUNT = 12,

    ROLE_PC = 20,
    ROLE_MO = 20,  // 默
    ROLE_LIN,      // 琳
    ROLE_AI,       // 艾
    ROLE_MENG,     // 梦
    ROLE_WEI,      // 薇
    ROLE_YI,       // 伊
    ROLE_MING,     // 冥
    ROLE_MIN,      // 命
    ROLE_WU,       // 舞
    ROLE_XI,       // 希
    ROLE_XIA,      // 霞
    ROLE_YA,       // 雅
    PC_COUNT = 12,

    ATTR_STR = 0, // 力量
    ATTR_AGI,     // 敏捷
    ATTR_INT,     // 智力
    ATTR_VIT,     // 体魄
    ATTR_SPR,     // 精神
    ATTR_MND,     // 意志
    ATTR_COUNT,

    GEAR_NONE = 0,
    GEAR_SWORD,     // 探险者之剑
    GEAR_BOW,       // 探险者短弓
    GEAR_STAFF,     // 探险者短杖
    GEAR_BLADE,     // 狂信者的荣誉之刃
    GEAR_ASSBOW,    // 反叛者的刺杀弓
    GEAR_DAGGER,    // 幽梦匕首
    GEAR_WAND,      // 光辉法杖
    GEAR_SHIELD,    // 荆棘盾剑
    GEAR_CLAYMORE,  // 陨铁重剑
    GEAR_SPEAR,     // 饮血魔剑
    GEAR_COLORFUL,  // 彩金长剑
    GEAR_LIMPIDWAND,// 清澄长杖
    GEAR_GLOVES,    // 探险者手环
    GEAR_BRACELET,  // 命师的传承手环
    GEAR_VULTURE,   // 秃鹫手环
    GEAR_RING,      // 海星戒指
    GEAR_DEVOUR,    // 噬魔戒指
    GEAR_PLATE,     // 探险者铁甲
    GEAR_LEATHER,   // 探险者皮甲
    GEAR_CLOTH,     // 探险者布甲
    GEAR_CLOAK,     // 旅法师的灵光袍
    GEAR_THORN,     // 战线支撑者的荆棘重甲
    GEAR_WOOD,      // 复苏战衣
    GEAR_CAPE,      // 挑战斗篷
    GEAR_SCARF,     // 探险者耳环
    GEAR_TIARA,     // 占星师的耳饰
    GEAR_RIBBON,    // 萌爪耳钉
    GEAR_HUNT,      // 猎魔耳环
    GEAR_COUNT,

    AURA_SHI = 0x00000001, // 启程之誓
    AURA_XIN = 0x00000002, // 启程之心
    AURA_FENG = 0x00000004, // 启程之风
    AURA_TIAO = 0x00000008, // 等级挑战
    AURA_YA = 0x00000010, // 等级压制
    AURA_BI = 0x00000020, // 破壁之心
    AURA_MO = 0x00000040, // 破魔之心
    AURA_DUN = 0x00000080, // 复合护盾
    AURA_XUE = 0x00000100, // 鲜血渴望
    AURA_XIAO = 0x00000200, // 削骨之痛
    AURA_SHENG = 0x00000400, // 圣盾祝福
    AURA_E = 0x00000800, // 恶意抽奖
    AURA_SHANG = 0x00001000, // 伤口恶化
    AURA_SHEN = 0x00002000, // 精神创伤
    AURA_CI = 0x00004000, // 铁甲尖刺
    AURA_REN = 0x00008000, // 忍无可忍
    AURA_RE = 0x00010000, // 热血战魂
    AURA_DIAN = 0x00020000, // 点到为止
    AURA_WU = 0x00040000, // 午时已到
    AURA_ZHI = 0x00080000, // 纸薄命硬
    AURA_SHAN = 0x00100000, // 不动如山
    AURA_FEI = 0x00200000, // 沸血之志
    AURA_BO = 0x00400000, // 波澜不惊
    AURA_JU = 0x00800000, // 飓风之力
    AURA_HONG = 0x01000000, // 红蓝双刺
    AURA_JUE = 0x02000000, // 荧光护盾
    AURA_HOU = 0x04000000, // 后发制人
    AURA_DUNH = 0x08000000, // 钝化锋芒
    AURA_ZI = 0x10000000, // 自信回头
    AURA_DI = 0x20000000, // 绝对底线(野怪专用)

    AURA_COUNT = 30,
    FLAG_STAT = 1 << AURA_COUNT,

    MYST_BLADE = 0x00001, // 暴击时附带(物理攻击力*50%)的绝对伤害
    MYST_ASSBOW = 0x00002, // 攻击附带(对方当前护盾值*30%)的物理伤害
    MYST_DAGGER = 0x00004, // 星火宝石的效果翻倍 血精宝石的伤害提升(星火*15%)
    MYST_WAND = 0x00008, // 魔力压制增加40%技能伤害，第一击必释放技能
    MYST_SHIELD = 0x00010, // 削弱对方40%的回血和回盾效果
    MYST_CLAYMORE = 0x00020, // 暴击率100%
    MYST_SPEAR = 0x00040, // 攻击附带(对方当前生命值*30%)的魔法伤害
    MYST_COLORFUL = 0x00080, // 彩金对剑无视对方情况同时附带物理和魔法伤害
    MYST_LIMPIDWAND = 0x00100, // 澄空之心额外获得(15%对方魔法防御)的魔法附加穿透。
    MYST_BRACELET = 0x00200, // 20%几率特殊暴击，魔法伤害增加100%
    MYST_VULTURE = 0x00400, // 额外增加20%对护盾的实际吸血给生命值
    MYST_RING = 0x00800, // 舞增加(锦上添花伤害的20%)的普通伤害
    MYST_DEVOUR = 0x01000, // 命运链接获得的护盾回复的50%添加到生命回复
    MYST_CLOAK = 0x02000, // 护盾最大值+35%
    MYST_THORN = 0x04000, // 增加25%固定伤害反弹
    MYST_WOOD = 0x08000, // 被攻击时回复(5%自身最大生命值)
    MYST_CAPE = 0x10000, // 被攻击回合时攻击方50%的物理伤害转换为魔法伤害
    MYST_TIARA = 0x20000, // 星芒之盾的护盾最大值提升至45%，减速效果提升至4%
    MYST_RIBBON = 0x40000, // 锁定元气无限为低于30%血量判定。
    MYST_HUNT = 0x80000, // 圣银弩箭30%物理攻击转换为绝对伤害

    PREF_SHANG = 0, // 诅咒=伤口恶化+精神创伤
    PREF_BO,        // 法神=破魔之心+波澜不惊
    PREF_FEI,       // 战神=破壁之心+沸血之志
    PREF_HOU,       // 隐忍=忍无可忍+后发制人
    PREF_JU,        // 疯狂=热血战魂+飓风之力
    PREF_HONG,      // 刺痛=削骨之痛+红蓝双刺
    PREF_DIAN,      // 坚韧=圣盾祝福+点到为止
    PREF_CI,        // 尖刺=鲜血渴望+铁甲尖刺
    PREF_JUE,       // 防盾=复合护盾+荧光护盾
    PREF_COUNT,

    WISH_HP_POT = 0, // 生命药水 生命低于??%时回复0.5%*W的生命值 最大100
    WISH_SLD_POT,    // 护盾药水 护盾低于??%时回复0.5%*W的护盾值 最大100
    WISH_SHI_BUF,    // 启程之誓强化 效果增加5%*W倍 最大100
    WISH_XIN_BUF,    // 启程之心强化 效果增加5%*W倍 最大100
    WISH_FENG_BUF,   // 启程之风强化 效果增加5%*W倍 最大100
    WISH_PATKA,      // 附加物伤增加5*W 最大1000
    WISH_MATKA,      // 附加魔伤增加5*W 最大1000
    WISH_HPM,        // 附加生命增加12*W 最大1000
    WISH_SLDM,       // 附加护盾增加20*W 最大1000
    WISH_SPDA,       // 附加攻速增加W 最大200
    WISH_PBRCA,      // 物理附加穿透增加W 最大200
    WISH_MBRCA,      // 魔法附加穿透增加W 最大200
    WISH_PDEFA,      // 物理附加防御增加W 最大200
    WISH_MDEFA,      // 魔法附加防御增加W 最大200
    WISH_COUNT,

    AMUL_STR = 0, // 力量
    AMUL_AGI,     // 敏捷
    AMUL_INT,     // 智力
    AMUL_VIT,     // 体魄
    AMUL_SPR,     // 精神
    AMUL_MND,     // 意志
    AMUL_PATK,    // 物理攻击
    AMUL_MATK,    // 魔法攻击
    AMUL_SPD,     // 攻击速度
    AMUL_REC,     // 回复效果
    AMUL_HP,      // 最大生命
    AMUL_SLD,     // 最大护盾
    AMUL_LCH,     // 生命偷取
    AMUL_RFL,     // 伤害反弹
    AMUL_CRT,     // 暴击几率
    AMUL_SKL,     // 技能几率
    AMUL_PDEF,    // 物理防御
    AMUL_MDEF,    // 魔法防御
    AMUL_AAA,     // 全属性
    AMUL_CRTR,    // 暴击抵抗
    AMUL_SKLR,    // 技能抵抗
    AMUL_COUNT,
};

struct BStat
{
    int role;    // 角色类型
    int lvl;     // 等级
    double hp;      // 当前生命
    double hpM;     // 最大生命
    double hpRecP;  // 百分比生命回复
    double hpRecA;  // 附加生命回复
    double hpRecRR; // 生命回复减少率(百分比)
    double pAtkB;   // 基础物理攻击
    double pAtkA;   // 附加物理攻击
    double pAtkR;   // 物理攻击增加率(百分比)
    double mAtkB;   // 基础魔法攻击
    double mAtkA;   // 附加魔法攻击
    double mAtkR;   // 魔法攻击增加率(百分比)
    double aAtk;    // 绝对攻击
    double spdB;    // 基础攻击速度
    double spdA;    // 附加攻击速度
    double spdRR;   // 减速倍率(百分比)
    double spdC;    // 速度计数
    double pBrcP;   // 百分比物理穿透
    double pBrcA;   // 附加物理穿透
    double mBrcP;   // 百分比魔法穿透
    double mBrcA;   // 附加魔法穿透
    double sRateB;  // 技能释放基数
    double sRateP;  // 技能释放率
    double cRateB;  // 暴击释放基数
    double cRateP;  // 暴击释放率
    double cBrcP;   // 百分比暴击穿透
    double lchP;    // 百分比生命偷取
    double pDefB;   // 基础物理防御
    double pDefA;   // 附加物理防御
    double mDefB;   // 基础魔法防御
    double mDefA;   // 附加魔法防御
    double pRdc;    // 物理减伤
    double mRdc;    // 魔法减伤
    double sld;     // 当前护盾
    double sldM;    // 最大护盾
    double sldRecP; // 百分比护盾回复
    double sldRecA; // 附加护盾回复
    double sldRecRR;// 护盾回复减少率(百分比)
    double rflP;    // 百分比伤害反弹
    double cDef;   // 基础暴击抵抗
    double sDef;   // 基础技能防御
    int psvSkl;  // 被动技能组合(光环、flag)
    int myst;    // 神秘属性组合 
    int sklC;    // 角色技能计数(星火、星芒、神秘法杖的初次技能、闪避充能、成长值、蛛网)
    int houC;    // 后发制人计数
    uint16_t wish[WISH_COUNT]; // 许愿池点数
    uint8_t amul[AMUL_COUNT]; // 护身符点数
    bool hpPot;  // 生命药水是否已使用
    bool sldPot; // 护盾药水是否已使用
    bool ziFlag; // 自信回头是否已发动

    int tStr; // 力量加点
    int tAgi; // 敏捷加点
    int tInt; // 智力加点
    int tVit; // 体魄加点
    int tSpr; // 精神加点
    int tMnd; // 意志加点

    int mode; // 雅状态 0白天1黑夜2凶神

    int atkLvl; // 进攻等级
    int defLvl; // 防御等级

    std::string alias;
};

struct Gear
{
    int type;
    int lvl;
    int percent[4];
    bool isMyst;
};

struct NonPlayer
{
    int role;
    int lvl;
    int prefixCount;
    int prefix;
};

struct Player
{
    int role;
    int lvl;
    int kfLvl;
    int sklSlot;
    int quality;
    int growth;
    int mode;
    int attr[ATTR_COUNT];
    int auraSkl;
    Gear gear[4];
    uint16_t wish[WISH_COUNT];
    uint8_t amul[AMUL_COUNT];
    int type;
    double weight;
    std::string alias;
    BStat* pBStat;
};

const char* const npcName[NPC_COUNT] = { "MU", "ZHU", "DENG", "SHOU", "MU2", "ZHU2", "DENG2", "SHOU2", "YU2", "HAO2", "LIU", "SHI" };
const char* const pcName[PC_COUNT] = { "MO", "LIN", "AI", "MENG", "WEI", "YI", "MING", "MIN", "WU", "XI", "XIA", "YA" };
const char* const gearName[GEAR_COUNT] = {
    "NONE", "SWORD", "BOW", "STAFF", "BLADE", "ASSBOW", "DAGGER", "WAND", "SHIELD",
    "CLAYMORE", "SPEAR", "COLORFUL", "LIMPIDWAND", "GLOVES", "BRACELET", "VULTURE", "RING", "DEVOUR", "PLATE",
    "LEATHER", "CLOTH", "CLOAK", "THORN", "WOOD", "CAPE", "SCARF", "TIARA", "RIBBON" , "HUNT" };
const int gearSlot[GEAR_COUNT] = { -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3 };
const char* const auraName[AURA_COUNT] = {
    "SHI", "XIN", "FENG", "TIAO", "YA",
    "BI", "MO", "DUN", "XUE", "XIAO", "SHENG", "E",
    "SHANG", "SHEN", "CI", "REN", "RE", "DIAN", "WU", "ZHI", "SHAN",
    "FEI", "BO", "JU", "HONG", "JUE", "HOU", "DUNH", "ZI",
    "DI" };
const int auraCost[AURA_COUNT] = {
    0, 0, 0, 0, 0,
    20, 20, 20, 20, 20, 20, 20,
    30, 30, 30, 30, 30, 30, 30, 30, 30,
    100, 100, 100, 100, 100, 100, 100, 100,
    0 };
int auraRandCount = 1;
int wishMax[WISH_COUNT] = { 100, 100, 100, 100, 100, 1000, 1000, 1000, 1000, 200, 200, 200, 200, 200 };
const char* const prefName[PREF_COUNT] = {
    "SHANG", "BO", "FEI", "HOU", "JU", "HONG", "DIAN", "CI", "JUE" };
const int prefAura[PREF_COUNT] = {
    AURA_SHANG | AURA_SHEN, AURA_MO | AURA_BO, AURA_BI | AURA_FEI,
    AURA_REN | AURA_HOU, AURA_RE | AURA_JU, AURA_XIAO | AURA_HONG,
    AURA_SHENG | AURA_DIAN, AURA_XUE | AURA_CI, AURA_DUN | AURA_JUE };
int prefCount[1 << PREF_COUNT][5];
int prefTable[1 << PREF_COUNT][5][PREF_COUNT * (PREF_COUNT - 1) * (PREF_COUNT - 2) * (PREF_COUNT - 3) / 24];
const char* const amulName[AMUL_COUNT] = {
    "STR", "AGI", "INT", "VIT", "SPR", "MND",
    "PATK", "MATK", "SPD", "REC", "HP", "SLD",
    "LCH", "RFL", "CRT", "SKL", "PDEF", "MDEF", "AAA", "CRTR", "SKLR" };
const int profitRate[4] = { 2, 3, 4, 6 }; // *50%

double sklRate[NPC_COUNT][2] = { {1.0, 1.0}, {3.0, 1.0}, {8.0, 1.0}, {1.0, 1.0},
                             {2.0, 1.0}, {5.0, 2.0}, {8.0, 1.0}, {1.0, 1.0}, {1.0, 1.0}, {1.0, 1.0},
                             {1.0, 1.0},
                             {4.0, 1.0}};
double crtRate[NPC_COUNT][2] = { {1.0, 1.0}, {1.0, 1.0}, {0.0, 1.0}, {3.0, 1.0},
                             {2.0, 1.0}, {2.0, 1.0}, {0.0, 1.0}, {3.0, 1.0}, {4.0, 1.0}, {0.0, 1.0},
                             {1.0, 1.0},
                             {4.0, 1.0}};

int auraMax;
Player myself;
int totalAttr;
std::vector<NonPlayer> npcEnemy;
std::vector<Player> pcEnemy;
std::vector<double> pcWeight;
std::vector<int> pcType; // 1:Atk 2:Def 3:All
int pcAtkCount = 0;
int pcDefCount = 0;
Player* lastPc = NULL;
std::vector<Gear> gears[4];
BStat myStat;
std::vector<BStat> npcEnemyStat;
std::vector<BStat> pcEnemyStat;

struct BResult
{
    int winner; // 0: attacker, 1: defender, 2: draw
    double rate; // (hp+sld)/(hpM+sldM) of winner, or 1 if draw
};

struct AttrKey
{
    int16_t at[ATTR_COUNT];
    int8_t gi[4];
    int32_t as;

    inline bool operator==(const AttrKey& o) const
    {
        return memcmp(this, &o, sizeof(AttrKey)) == 0;
    }

    inline bool operator<(const AttrKey& o) const
    {
        return memcmp(this, &o, sizeof(AttrKey)) < 0;
    }

    void print() const
    {
        for (int i = 0; i < ATTR_COUNT; ++i)
        {
            printf("%d ", (int)at[i]);
        }
        printf("\n");
        for (int i = 0; i < 4; ++i)
        {
            const Gear& gear = gears[i][gi[i]];
            printf("%s", gearName[gear.type]);
            if (gear.type != GEAR_NONE)
            {
                printf(" %d %d %d %d %d %d", gear.lvl, gear.percent[0], gear.percent[1], gear.percent[2], gear.percent[3], gear.isMyst ? 1 : 0);
            }
            printf("\n");
        }
        int auraCount = 0;
        for (int i = 0; i < AURA_COUNT; ++i)
        {
            if (as & 1 << i) ++auraCount;
        }
        printf("%d", auraCount);
        for (int i = 0; i < AURA_COUNT; ++i)
        {
            if (as & 1 << i) printf(" %s", auraName[i]);
        }
        printf("\n");
    }
};

struct AttrKeyHash
{
    inline size_t operator()(const AttrKey& key) const
    {
        return crc64r(&key, sizeof(AttrKey));
    }
};

struct AttrScore
{
    double v1, v2;

    explicit AttrScore(double v1 = -1, double v2 = 0) : v1(v1), v2(v2)
    {
    }

    inline bool operator<(const AttrScore& o) const
    {
        return v1 != o.v1 ? v1 < o.v1 : v2 < o.v2;
    }

    inline int comp(const AttrScore& o) const
    {
        return v1 < o.v1 ? -1 : v1 > o.v1 ? 1 : v2 < o.v2 ? -1 : v2 > o.v2 ? 1 : 0;
    }
};

typedef std::pair<AttrKey, AttrScore> AttrPair;

struct AttrPairComp
{
    inline bool operator()(const AttrPair& a, const AttrPair& b) const
    {
        int c = a.second.comp(b.second);
        return c ? c > 0 : memcmp(&a.first, &b.first, sizeof(AttrKey)) < 0;
    }
};

typedef std::tr1::unordered_map<AttrKey, AttrScore, AttrKeyHash> AttrMap;
typedef std::priority_queue<AttrPair, std::vector<AttrPair>, AttrPairComp> AttrQueue;

std::vector<AttrKey> attrSeed;
int initStep;
int64_t attrSeedTotal;
const int speedReduceMax = 80;

char buf[10000];
int version = 506;
int rseedGlobal = time(NULL);
int numThreads = 4;
int numTests = 1000;
double ciTest = 0;
int gridSize = 6;
int stepRate = 3;
int candidateMax = 20;
int startLevel = 0;
int reduceRateA = 3;
int reduceRateB = 10;
int pcWeightA = 1;
int pcWeightB = 1;
int maxAttr[ATTR_COUNT] = {};
int attrSeedMax = 1000000;
int auraFilter = AURA_DI;
bool verbose = false;
int defMode = 0; // 0:off 1:on 2:mix
bool debug = false;

pthread_mutex_t threadMutex = PTHREAD_MUTEX_INITIALIZER;
pthread_cond_t attrEvalTaskCond = PTHREAD_COND_INITIALIZER;
pthread_cond_t attrEvalTaskFullCond = PTHREAD_COND_INITIALIZER;
pthread_cond_t attrEvalFinishCond = PTHREAD_COND_INITIALIZER;
pthread_cond_t progressMeterFinishCond = PTHREAD_COND_INITIALIZER;
pthread_attr_t threadAttr;
volatile bool attrEvalWorking;
volatile bool progressMeterWorking;
volatile bool progressMeterAlive;
volatile bool signalCatch = false;
volatile int attrEvalAliveCount;
volatile int attrEvalWorkingCount;
volatile int calcAttrStage;
volatile int calcAttrCount;
volatile double bestWinRate;
volatile double bestProfit;
timeval calcAttrTvBegin;

void signalHandler(int sig)
{
    signalCatch = true;
}

void ci(int s, int n, double& low, double& high)
{
    if (n == 0)
    {
        low = 0.0;
        high = 1.0;
        return;
    }
    double z = 1.959964; // 95%
    double a = 1.0 * s / n;
    double c = 2 * n * a + z * z;
    double r = sqrt(4 * n * a * (1 - a) + z * z) * z;
    double t = 2 * (n + z * z);
    low = (s == 0 ? 0.0 : (c - r) / t);
    high = (s == n ? 1.0 : (c + r) / t);
}

int revMul(int a, double x)
{
    int b = a / x;
    while (int(b * x) <= a) ++b;
    return --b;
}

int gcd(int a, int b)
{
    while (a && b)
    {
        int c = a % b;
        a = b;
        b = c;
    }
    return a + b;
}

void initPrefTable()
{
    memset(prefCount, 0, sizeof(prefCount));
    for (int i = 0; i < 1 << PREF_COUNT; ++i)
    {
        int auraSkl = 0;
        int prefN = 0;
        for (int j = 0; j < PREF_COUNT; ++j)
        {
            if (i & (1 << j))
            {
                ++prefN;
                auraSkl |= prefAura[j];
            }
        }
        if (prefN <= 4)
        {
            for (int j = 0; j <= i; ++j)
            {
                if ((j & i) == j)
                {
                    prefTable[j][prefN][prefCount[j][prefN]++] = auraSkl;
                }
            }
        }
        for (int j = 0; j < prefN && j <= 4; ++j)
        {
            prefCount[i][j] = 1;
            prefTable[i][j][0] = auraSkl;
        }
    }

    auraRandCount = 1;
    for (int i = 0; i < 1 << PREF_COUNT; ++i)
    {
        for (int j = 0; j <= 4; ++j)
        {
            auraRandCount = auraRandCount * prefCount[i][j] / gcd(auraRandCount, prefCount[i][j]);
        }
    }
}

class ProgressMeter
{
public:
    void init(int initSeed, int initStep)
    {
        mInitSeed = initSeed;
        mTotalStep = 0;
        while (initStep > 0)
        {
            ++mTotalStep;
            initStep = initStep * (stepRate - 1) / stepRate;
        }
        mFirstRate = 1.0 * initSeed / (initSeed + mTotalStep * 1000);
        mSecondRate = (1 - mFirstRate) / mTotalStep;
    }

    double getProgress(int s, int c)
    {
        if (s < 0)
        {
            return 1.0 * c / mInitSeed * mFirstRate;
        }
        else
        {
            double p = c / 50.0;
            p = (p + 11 - sqrt(p * p - 18 * p + 121)) / 20;
            return mSecondRate * (s + p) + mFirstRate;
        }
    }

protected:
    int mInitSeed;
    int mTotalStep;
    double mFirstRate;
    double mSecondRate;
};

ProgressMeter pm;

inline int myrand(int* rseed, int m)
{
    const int M = 48271;
    const int Q = 0x7FFFFFFF / M;
    const int R = 0x7FFFFFFF % M;
    *rseed = M * (*rseed % Q) - R * (*rseed / Q);
    if (*rseed < 0) *rseed += 0x7FFFFFFF;
    return *rseed % m;
}

inline int64_t myrand64(int* rseed, int64_t m)
{
    if (m <= 0x7FFFFFFF) return myrand(rseed, m);
    int64_t r = static_cast<int64_t>(myrand(rseed, 0x40000000)) << 30;
    r |= myrand(rseed, 0x40000000);
    return r % m;
}

inline int rand100(int* rseed)
{
    return myrand(rseed, 100);
}

bool isNumberDot(const char* s)
{
    for (; *s; ++s) if ((*s < '0' || *s > '9') && *s != '.') return false;
    return true;
}

bool isNumber(const char* s)
{
    for (; *s; ++s) if (*s < '0' || *s > '9') return false;
    return true;
}

bool getNpcRolePrefix(char* str, int& role, int& prefix)
{
    role = -1;
    prefix = 0;
    char* p = strchr(str, '_');
    if (p) *p = 0;
    for (int i = 0; i < NPC_COUNT; ++i)
    {
        if (strcmp(str, npcName[i]) == 0)
        {
            role = ROLE_NPC + i;
            break;
        }
    }
    if (role == -1) return false;
    if (role == ROLE_LIU)
    {
        //  0-11: category
        // 12-17: hpM
        // 18-23: sldM
        // 24-26: pAtk
        // 27-29: mAtk
        if (!p)
        {
            prefix = 0x3FFFFFFF;
        }
        else
        {
            ++p;
            if (strlen(p) != 16) return false;
#define GET_NUM(res, s, l, min, max) \
    do \
    { \
        int qcount = 0; \
        res = 0; \
        for (int j = s; j < s + l; ++j) \
        { \
            if (p[j] == '?') \
            { \
                ++qcount; \
            } \
            else if (p[j] >= '0' && p[j] <= '9') \
            { \
                res = res * 10 + (p[j] - '0'); \
            } \
            else \
            { \
                res = -1; \
                break; \
            } \
        } \
        if (qcount == l) res = -2; \
        else if (qcount > 0) res = -1; \
        else if (res < min || res > max) res = -1; \
    } \
    while (false)
            int res;
            for (int i = 0; i < 6; ++i)
            {
                GET_NUM(res, i, 1, 0, 2);
                if (res == -1) return false;
                prefix |= (res == -2 ? 3 : res) << (i * 2);
            }
            for (int i = 0; i < 2; ++i)
            {
                GET_NUM(res, i * 3 + 6, 3, 280, 320);
                if (res == -1) return false;
                prefix |= (res == -2 ? 63 : res - 280) << (i * 6 + 12);
            }
            for (int i = 0; i < 2; ++i)
            {
                GET_NUM(res, i * 2 + 12, 2, 28, 32);
                if (res == -1) return false;
                prefix |= (res == -2 ? 7 : res - 28) << (i * 3 + 24);
            }
#undef GET_NUM
        }
    }
    else
    {
        while (p)
        {
            char* next = strchr(p + 1, '_');
            if (next) *next = 0;
            bool found = false;
            for (int i = 0; i < PREF_COUNT; ++i)
            {
                if (strcmp(p + 1, prefName[i]) == 0)
                {
                    prefix |= 1 << i;
                    found = true;
                    break;
                }
            }
            if (!found) return false;
            *p = 0;
            p = next;
        }
    }
    return true;
}

bool readGear(FILE* fp, Gear& gear)
{
    long pos = ftell(fp);

    for (;;)
    {
        if (fscanf(fp, "%s", buf) != 1)
        {
            fseek(fp, pos, SEEK_SET);
            return false;
        }
        if (buf[0] == '/' && buf[1] == '/')
        {
            fgets(buf, sizeof(buf), fp);
            pos = ftell(fp);
            continue;
        }
        break;
    }
    gear.type = -1;
    for (int i = 0; i < GEAR_COUNT; ++i)
    {
        if (strcmp(buf, gearName[i]) == 0)
        {
            gear.type = i;
            break;
        }
    }
    if (gear.type == -1)
    {
        fseek(fp, pos, SEEK_SET);
        return false;
    }
    if (gear.type != GEAR_NONE)
    {
        int b;
        if (fscanf(fp, "%d%d%d%d%d%d", &gear.lvl, &gear.percent[0], &gear.percent[1],
            &gear.percent[2], &gear.percent[3], &b) != 6 ||
            gear.lvl < 1 ||
            gear.percent[0] < 50 || gear.percent[0] > 150 ||
            gear.percent[1] < 50 || gear.percent[1] > 150 ||
            gear.percent[2] < 50 || gear.percent[2] > 150 ||
            gear.percent[3] < 50 || gear.percent[3] > 150 ||
            b < 0 || b > 1)
        {
            fseek(fp, pos, SEEK_SET);
            return false;
        }
        gear.isMyst = (b == 1);
    }
    return true;
}

bool readNonPlayer(FILE* fp, NonPlayer& npc)
{
    long pos = ftell(fp);

    for (;;)
    {
        if (fscanf(fp, "%s", buf) != 1)
        {
            fseek(fp, pos, SEEK_SET);
            return false;
        }
        if (buf[0] == '/' && buf[1] == '/')
        {
            fgets(buf, sizeof(buf), fp);
            pos = ftell(fp);
            continue;
        }
        break;
    }
    if (!getNpcRolePrefix(buf, npc.role, npc.prefix))
    {
        fseek(fp, pos, SEEK_SET);
        return false;
    }
    if (fscanf(fp, "%d%d", &npc.lvl, &npc.prefixCount) != 2 || npc.lvl < 1 ||
        npc.prefixCount < 0 || npc.prefixCount > 4)
    {
        fseek(fp, pos, SEEK_SET);
        return false;
    }
    return true;
}

bool readPlayer(FILE* fp, Player& pc)
{
    long pos = ftell(fp);

    for (;;)
    {
        if (fscanf(fp, "%s", buf) != 1)
        {
            fseek(fp, pos, SEEK_SET);
            return false;
        }
        if (buf[0] == '/' && buf[1] == '/')
        {
            fgets(buf, sizeof(buf), fp);
            pos = ftell(fp);
            char* p = strstr(buf, " level:");
            if (p && lastPc && lastPc->pBStat)
            {
                int lvl;
                if (sscanf(p + 7, "%d", &lvl) == 1 && lvl >= 1)
                {
                    lastPc->lvl = lvl;
                    lastPc->pBStat->lvl = lvl;
                }
            }
            lastPc = NULL;
            continue;
        }
        break;
    }
    pc.weight = 1;
    pc.type = 3;
    if (strcmp(buf, "ATK") == 0)
    {
        pc.type = 1;
        if (fscanf(fp, "%s", buf) != 1)
        {
            printf("Error: EOF after \"ATK\"\n");
            fseek(fp, pos, SEEK_SET);
            return false;
        }
    }
    else if (strcmp(buf, "DEF") == 0)
    {
        pc.type = 2;
        if (fscanf(fp, "%s", buf) != 1)
        {
            printf("Error: EOF after \"DEF\"\n");
            fseek(fp, pos, SEEK_SET);
            return false;
        }
    }
    if (buf[0] == 'W' && buf[1] == '=' && isNumberDot(buf + 2))
    {
        if (sscanf(buf + 2, "%lf", &pc.weight) != 1)
        {
            printf("Error: Invalid \"W=\" parameter: %s\n", buf + 2);
            fseek(fp, pos, SEEK_SET);
            return false;
        }
        if (fscanf(fp, "%s", buf) != 1)
        {
            printf("Error: EOF after \"W=\"\n");
            fseek(fp, pos, SEEK_SET);
            return false;
        }
    }
    char* p = strchr(buf, '_');
    if (p != NULL)
    {
        pc.alias = p + 1;
        *p = 0;
    }
    pc.role = -1;
    for (int i = 0; i < PC_COUNT; ++i)
    {
        if (strcmp(buf, pcName[i]) == 0)
        {
            pc.role = ROLE_PC + i;
            break;
        }
    }
    if (pc.role == -1)
    {
        printf("Error: Unknown PC role name: %s\n", buf);
        fseek(fp, pos, SEEK_SET);
        return false;
    }
    if (fscanf(fp, "%s", buf) != 1)
    {
        printf("Error: EOF after PC role name\n");
        fseek(fp, pos, SEEK_SET);
        return false;
    }
    if (buf[0] == 'G' && buf[1] == '=')
    {
        if (!isNumber(buf + 2) || sscanf(buf + 2, "%d", &pc.growth) != 1 ||
            pc.growth < 0)
        {
            printf("Error: Invalid \"G=\" parameter: %s\n", buf + 2);
            fseek(fp, pos, SEEK_SET);
            return false;
        }
        if (fscanf(fp, "%s", buf) != 1)
        {
            printf("Error: EOF after \"G=\"\n");
            fseek(fp, pos, SEEK_SET);
            return false;
        }
    }
    else
    {
        pc.growth = 0;
    }
    if (buf[0] == 'M' && buf[1] == '=')
    {
        if (!isNumber(buf + 2) || sscanf(buf + 2, "%d", &pc.mode) != 1 ||
            pc.mode < 0 || pc.mode > 1)
        {
            printf("Error: Invalid \"M=\" parameter: %s\n", buf + 2);
            fseek(fp, pos, SEEK_SET);
            return false;
        }
        if (fscanf(fp, "%s", buf) != 1)
        {
            printf("Error: EOF after \"M=\"\n");
            fseek(fp, pos, SEEK_SET);
            return false;
        }
    }
    else
    {
        pc.mode = 0;
    }
    if (strcmp(buf, "STAT") == 0)
    {
        pc.pBStat = new BStat();
        BStat& b = *pc.pBStat;
        if (fscanf(fp, "%s", buf) != 1)
        {
            fseek(fp, pos, SEEK_SET);
            return false;
        }
        if (strcmp(buf, "WISH") == 0)
        {
            for (int i = 0; i < WISH_COUNT; ++i)
            {
                int w = 0;
                if (fscanf(fp, "%d", &w) != 1 || w < 0 || w > wishMax[i])
                {
                    fseek(fp, pos, SEEK_SET);
                    return false;
                }
                b.wish[i] = w;
            }
            if (fscanf(fp, "%s", buf) != 1)
            {
                fseek(fp, pos, SEEK_SET);
                return false;
            }
        }
        else
        {
            for (int i = 0; i < WISH_COUNT; ++i)
            {
                b.wish[i] = 0;
            }
        }
        for (int i = 0; i < AMUL_COUNT; ++i)
        {
            b.amul[i] = 0;
        }
        if (strcmp(buf, "AMULET") == 0)
        {
            for (;;)
            {
                if (fscanf(fp, "%s", buf) != 1)
                {
                    fseek(fp, pos, SEEK_SET);
                    return false;
                }
                if (strcmp(buf, "ENDAMULET") == 0)
                {
                    break;
                }
                bool found = false;
                for (int i = 0; i < AMUL_COUNT; ++i)
                {
                    if (strcmp(buf, amulName[i]) == 0)
                    {
                        int a = 0;
                        if (fscanf(fp, "%d", &a) != 1 ||
                            a < 0 || a >(i <= AMUL_MND ? 80 : 10) || b.amul[i] != 0)
                        {
                            fseek(fp, pos, SEEK_SET);
                            return false;
                        }
                        b.amul[i] = a;
                        found = true;
                        break;
                    }
                }
                if (!found)
                {
                    fseek(fp, pos, SEEK_SET);
                    return false;
                }
            }
            if (fscanf(fp, "%s", buf) != 1)
            {
                fseek(fp, pos, SEEK_SET);
                return false;
            }
        }
        if (!isNumber(buf) || sscanf(buf, "%d", &b.pAtkB) != 1)
        {
            fseek(fp, pos, SEEK_SET);
            return false;
        }
        int mAtkAdd = -1;
        if (fscanf(fp, "%d%s", &b.mAtkB, buf) != 2)
        {
            fseek(fp, pos, SEEK_SET);
            return false;
        }
        if (buf[0] == 'M' && buf[1] == '+' && isNumber(buf + 2))
        {
            if (sscanf(buf + 2, "%d", &mAtkAdd) != 1 || fscanf(fp, "%d", &b.aAtk) != 1)
            {
                fseek(fp, pos, SEEK_SET);
                return false;
            }
        }
        else if (buf[0] == 'M' && buf[1] == 'A' && buf[2] == '=' && isNumber(buf + 3))
        {
            int mAtkPlus = 0;
            if (sscanf(buf + 3, "%d", &mAtkPlus) != 1 || fscanf(fp, "%d", &b.aAtk) != 1 ||
                mAtkPlus > b.mAtkB)
            {
                fseek(fp, pos, SEEK_SET);
                return false;
            }
            b.mAtkB -= mAtkPlus;
            b.mAtkA = mAtkPlus;
        }
        else
        {
            b.mAtkA = 0;
            if (!isNumber(buf) || sscanf(buf, "%d", &b.aAtk) != 1)
            {
                fseek(fp, pos, SEEK_SET);
                return false;
            }
        }
        if (fscanf(fp, "%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d",
            &b.pBrcP, &b.pBrcA, &b.mBrcP, &b.mBrcA, &b.cBrcP,
            &b.spdB, &b.pDefB, &b.pRdc, &b.mDefB, &b.mRdc,
            &b.hpM, &b.hpRecP, &b.hpRecA, &b.sldM, &b.sldRecP, &b.sldRecA,
            &b.cRateB, &b.sRateB, &b.rflP, &b.lchP) != 20)
        {
            fseek(fp, pos, SEEK_SET);
            return false;
        }
        b.psvSkl = 0;
        b.myst = 0;
        int sklCount;
        if (fscanf(fp, "%d", &sklCount) != 1 || sklCount < 0)
        {
            fseek(fp, pos, SEEK_SET);
            return false;
        }
        pc.auraSkl = 0;
        b.psvSkl = FLAG_STAT;
        for (int i = 0; i < sklCount; ++i)
        {
            if (fscanf(fp, "%s", buf) != 1)
            {
                fseek(fp, pos, SEEK_SET);
                return false;
            }
            bool found = false;
            for (int j = 0; j < AURA_COUNT; ++j)
            {
                if (strcmp(buf, auraName[j]) == 0)
                {
                    pc.auraSkl |= 1 << j;
                    b.psvSkl |= 1 << j;
                    found = true;
                    break;
                }
            }
            if (found) continue;
            else if (strcmp(buf, "BLADE") == 0) b.myst |= MYST_BLADE;
            else if (strcmp(buf, "ASSBOW") == 0) b.myst |= MYST_ASSBOW;
            else if (strcmp(buf, "DAGGER") == 0) b.myst |= MYST_DAGGER;
            else if (strcmp(buf, "WAND") == 0) b.myst |= MYST_WAND;
            else if (strcmp(buf, "SHIELD") == 0) b.myst |= MYST_SHIELD;
            else if (strcmp(buf, "CLAYMORE") == 0) b.myst |= MYST_CLAYMORE;
            else if (strcmp(buf, "SPEAR") == 0) b.myst |= MYST_SPEAR;
            else if (strcmp(buf, "COLORFUL") == 0) b.myst |= MYST_COLORFUL;
            else if (strcmp(buf, "LIMPIDWAND") == 0) b.myst |= MYST_LIMPIDWAND;
            else if (strcmp(buf, "BRACELET") == 0) b.myst |= MYST_BRACELET;
            else if (strcmp(buf, "RING") == 0) b.myst |= MYST_RING;
            else if (strcmp(buf, "DEVOUR") == 0) b.myst |= MYST_DEVOUR;
            else if (strcmp(buf, "VULTURE") == 0) b.myst |= MYST_VULTURE;
            else if (strcmp(buf, "WOOD") == 0) b.myst |= MYST_WOOD;
            else if (strcmp(buf, "CAPE") == 0) b.myst |= MYST_CAPE;
            else if (strcmp(buf, "TIARA") == 0) b.myst |= MYST_TIARA;
            else if (strcmp(buf, "RIBBON") == 0) b.myst |= MYST_RIBBON;
            else
            {
                fseek(fp, pos, SEEK_SET);
                return false;
            }
        }
        b.role = pc.role;
        b.lvl = pc.lvl = -1;
        b.hp = b.hpM;
        b.hpRecRR = 0;
        b.pAtkA = 0;
        if (mAtkAdd != -1)
        {
            b.mAtkA = b.mAtkB - b.sRateB * 12 * (100 + mAtkAdd) / 100;
            if (b.mAtkA < 0) b.mAtkA = 0;
            b.mAtkB -= b.mAtkA;
        }
        b.spdA = 0;
        b.spdRR = 0;
        b.spdC = b.spdB;
        b.sRateP = b.sRateB * 100 / (b.sRateB + 99);
        b.cRateP = b.cRateB * 100 / (b.cRateB + 99);
        b.pDefA = 0;
        b.mDefA = 0;
        b.sld = b.sldM;
        b.sldRecRR = 0;
        b.sklC = (b.role == ROLE_MIN ? 1 : b.role == ROLE_WU ? (pc.growth > 106800 ? 106800 : pc.growth) : 0);
        b.houC = 0;
        b.alias = pc.alias;
    }
    else
    {
        if (sscanf(buf, "%d", &pc.lvl) != 1 ||
            fscanf(fp, "%d", &pc.kfLvl) != 1 ||
            fscanf(fp, "%d", &pc.sklSlot) != 1 ||
            fscanf(fp, "%d", &pc.quality) != 1 ||
            pc.lvl < 0 || pc.kfLvl < 0 || pc.sklSlot < 1 || pc.sklSlot > 7 ||
            pc.quality < 0 || pc.quality > 11)
        {
            fseek(fp, pos, SEEK_SET);
            return false;
        }
        if (fscanf(fp, "%s", buf) != 1)
        {
            fseek(fp, pos, SEEK_SET);
            return false;
        }
        if (strcmp(buf, "WISH") == 0)
        {
            for (int i = 0; i < WISH_COUNT; ++i)
            {
                int w = 0;
                if (fscanf(fp, "%d", &w) != 1 || w < 0 || w > wishMax[i])
                {
                    fseek(fp, pos, SEEK_SET);
                    return false;
                }
                pc.wish[i] = w;
            }
            if (fscanf(fp, "%s", buf) != 1)
            {
                fseek(fp, pos, SEEK_SET);
                return false;
            }
        }
        else
        {
            for (int i = 0; i < WISH_COUNT; ++i)
            {
                pc.wish[i] = 0;
            }
        }
        for (int i = 0; i < AMUL_COUNT; ++i)
        {
            pc.amul[i] = 0;
        }
        if (strcmp(buf, "AMULET") == 0)
        {
            for (;;)
            {
                if (fscanf(fp, "%s", buf) != 1)
                {
                    fseek(fp, pos, SEEK_SET);
                    return false;
                }
                if (strcmp(buf, "ENDAMULET") == 0)
                {
                    break;
                }
                bool found = false;
                for (int i = 0; i < AMUL_COUNT; ++i)
                {
                    if (strcmp(buf, amulName[i]) == 0)
                    {
                        int a = 0;
                        if (fscanf(fp, "%d", &a) != 1 ||
                            a < 0 || a >(i <= AMUL_MND ? 80 : 10) || pc.amul[i] != 0)
                        {
                            fseek(fp, pos, SEEK_SET);
                            return false;
                        }
                        pc.amul[i] = a;
                        found = true;
                        break;
                    }
                }
                if (!found)
                {
                    fseek(fp, pos, SEEK_SET);
                    return false;
                }
            }
            if (fscanf(fp, "%s", buf) != 1)
            {
                fseek(fp, pos, SEEK_SET);
                return false;
            }
        }
        if (!isNumber(buf) || sscanf(buf, "%d", &pc.attr[0]) != 1 || pc.attr[0] < 1)
        {
            fseek(fp, pos, SEEK_SET);
            return false;
        }
        int attrSum = pc.attr[0];
        for (int i = 1; i < ATTR_COUNT; ++i)
        {
            if (fscanf(fp, "%d", &pc.attr[i]) != 1 || pc.attr[i] < 1)
            {
                fseek(fp, pos, SEEK_SET);
                return false;
            }
            attrSum += pc.attr[i];
        }
        if (attrSum > (pc.lvl * 3 + 6) * (100 + pc.quality) / 100)
        {
            fseek(fp, pos, SEEK_SET);
            return false;
        }
        for (int i = 0; i < 4; ++i)
        {
            if (!readGear(fp, pc.gear[i]) ||
                (pc.gear[i].type != GEAR_NONE && gearSlot[pc.gear[i].type] != i))
            {
                fseek(fp, pos, SEEK_SET);
                return false;
            }
        }
        int sklCount;
        if (fscanf(fp, "%d", &sklCount) != 1 || sklCount < 0 || sklCount > pc.sklSlot)
        {
            fseek(fp, pos, SEEK_SET);
            return false;
        }
        pc.auraSkl = 0;
        for (int i = 0; i < sklCount; ++i)
        {
            if (fscanf(fp, "%s", buf) != 1)
            {
                fseek(fp, pos, SEEK_SET);
                return false;
            }
            bool found = false;
            for (int j = 0; j < AURA_COUNT; ++j)
            {
                if (strcmp(buf, auraName[j]) == 0)
                {
                    pc.auraSkl |= 1 << j;
                    found = true;
                    break;
                }
            }
            if (!found)
            {
                fseek(fp, pos, SEEK_SET);
                return false;
            }
        }
        pc.pBStat = NULL;
    }
    return true;
}

void readConfig(const char* fileName)
{
    FILE* fp = fopen(fileName ? fileName : "newkf.in", "rb");
    if (!fp)
    {
        printf("Cannot open config file %s\n", fileName ? fileName : "newkf.in");
        exit(-1);
    }
    if (fscanf(fp, "%d", &auraMax) != 1 || auraMax < 0 || auraMax > 400)
    {
        printf("Error reading aura data\n");
        exit(-1);
    }

    lastPc = NULL;
    if (!readPlayer(fp, myself))
    {
        printf("Error reading user player data\n");
        exit(-1);
    }
    if (myself.pBStat)
    {
        printf("Error: Cannot use STAT mode for player's PC\n");
        exit(-1);
    }
    int auraSum = 0;
    for (int i = 0; i < AURA_COUNT; ++i)
    {
        if (myself.auraSkl & (1 << i)) auraSum += auraCost[i];
    }
    if (auraSum > auraMax)
    {
        printf("Error: Player's passive skill cost larger than aura\n");
        exit(-1);
    }
    for (int i = 0; i < 4; ++i)
    {
        gears[i].push_back(myself.gear[i]);
    }
    totalAttr = (myself.lvl + 2) * 3 * (100 + myself.quality) / 100;
    for (int i = 0; i < ATTR_COUNT; ++i)
    {
        maxAttr[i] = totalAttr - ATTR_COUNT + 1;
    }

    for (;;)
    {
        if (fscanf(fp, "%s", buf) != 1) break;
        if (strcmp(buf, "NPC") == 0)
        {
            for (;;)
            {
                NonPlayer npc;
                if (!readNonPlayer(fp, npc))
                {
                    if (fscanf(fp, "%s", buf) != 1 || strcmp(buf, "ENDNPC") != 0)
                    {
                        printf("Error reading NPC enemy data\n");
                        exit(-1);
                    }
                    break;
                }
                npcEnemy.push_back(npc);
            }
        }
        else if (strcmp(buf, "PC") == 0)
        {
            lastPc = NULL;
            for (;;)
            {
                Player pc;
                if (!readPlayer(fp, pc))
                {
                    if (fscanf(fp, "%s", buf) != 1 || strcmp(buf, "ENDPC") != 0)
                    {
                        printf("Error reading PC enemy data\n");
                        exit(-1);
                    }
                    break;
                }
                pcEnemy.push_back(pc);
                lastPc = &pcEnemy.back();
                if (pc.type & 1) ++pcAtkCount;
                if (pc.type & 2) ++pcDefCount;
            }
        }
        else if (strcmp(buf, "GEAR") == 0)
        {
            for (;;)
            {
                Gear gear;
                if (!readGear(fp, gear))
                {
                    if (fscanf(fp, "%s", buf) != 1 || strcmp(buf, "ENDGEAR") != 0)
                    {
                        printf("Error reading extra gear data\n");
                        exit(-1);
                    }
                    break;
                }
                if (gear.type == GEAR_NONE)
                {
                    printf("Error reading extra gear data\n");
                    exit(-1);
                }
                gears[gearSlot[gear.type]].push_back(gear);
                if (gears[gearSlot[gear.type]].size() > 255)
                {
                    printf("Too many candidate gears\n");
                    exit(-1);
                }
            }
        }
        else if (strcmp(buf, "THREADS") == 0)
        {
            if (fscanf(fp, "%d", &numThreads) != 1 || numThreads < 1 || numThreads > 64)
            {
                printf("Error reading THREADS setting\n");
                exit(-1);
            }
        }
        else if (strcmp(buf, "TESTS") == 0)
        {
            if (fscanf(fp, "%d", &numTests) != 1 || numTests < 1 || numTests > 100000000)
            {
                printf("Error reading TESTS setting\n");
                exit(-1);
            }
        }
        else if (strcmp(buf, "CITEST") == 0)
        {
            if (fscanf(fp, "%lf", &ciTest) != 1 || ciTest < 0 || ciTest > 100)
            {
                printf("Error reading CITEST setting\n");
                exit(-1);
            }
            ciTest /= 100;
        }
        else if (strcmp(buf, "STARTLEVEL") == 0)
        {
            if (fscanf(fp, "%d", &startLevel) != 1 || startLevel < 0 || startLevel > 88)
            {
                printf("Error reading STARTLEVEL setting\n");
                exit(-1);
            }
        }
        else if (strcmp(buf, "REDUCERATE") == 0)
        {
            if (fscanf(fp, "%d%d", &reduceRateA, &reduceRateB) != 2 ||
                reduceRateA < 0 || reduceRateB < 1 || reduceRateA > reduceRateB)
            {
                printf("Error reading REDUCERATE setting\n");
                exit(-1);
            }
        }
        else if (strcmp(buf, "PCWEIGHT") == 0)
        {
            if (fscanf(fp, "%d%d", &pcWeightA, &pcWeightB) != 2 ||
                pcWeightA < 1 || pcWeightB < 1)
            {
                printf("Error reading PCWEIGHT setting\n");
                exit(-1);
            }
        }
        else if (strcmp(buf, "MAXATTR") == 0)
        {
            int sum = 0;
            for (int i = 0; i < ATTR_COUNT; ++i)
            {
                if (fscanf(fp, "%d", &maxAttr[i]) != 1 || maxAttr[i] < 0 ||
                    (maxAttr[i] > 0 && maxAttr[i] < myself.attr[i]))
                {
                    printf("Error reading MAXATTR setting\n");
                    exit(-1);
                }
                if (maxAttr[i] == 0 || maxAttr[i] > totalAttr - ATTR_COUNT + 1)
                {
                    maxAttr[i] = totalAttr - ATTR_COUNT + 1;
                }
                sum += maxAttr[i];
            }
            if (sum < totalAttr)
            {
                printf("Error reading MAXATTR setting\n");
                exit(-1);
            }
        }
        else if (strcmp(buf, "SEEDMAX") == 0)
        {
            if (fscanf(fp, "%d", &attrSeedMax) != 1 ||
                attrSeedMax < 1 || attrSeedMax > 100000000)
            {
                printf("Error reading SEEDMAX setting\n");
                exit(-1);
            }
        }
        else if (strcmp(buf, "AURAFILTER") == 0)
        {
            if (fscanf(fp, "%s", buf) != 1)
            {
                printf("Error reading AURAFILTER setting\n");
                exit(-1);
            }
            char* tok = strtok(buf, "_");
            while (tok)
            {
                bool found = false;
                for (int i = 0; i < AURA_COUNT; ++i)
                {
                    if (strcmp(tok, auraName[i]) == 0)
                    {
                        auraFilter |= 1 << i;
                        found = true;
                        break;
                    }
                }
                if (!found)
                {
                    printf("Error reading AURAFILTER setting\n");
                    exit(-1);
                }
                tok = strtok(NULL, "_");
            }
        }
        else if (strcmp(buf, "DEFENDER") == 0)
        {
            int x;
            if (fscanf(fp, "%d", &x) != 1 || x < 0 || x > 2)
            {
                printf("Error reading DEFENDER setting\n");
                exit(-1);
            }
            defMode = x;
        }
        else if (strcmp(buf, "VERBOSE") == 0)
        {
            int x;
            if (fscanf(fp, "%d", &x) != 1 || x < 0 || x > 1)
            {
                printf("Error reading VERBOSE setting\n");
                exit(-1);
            }
            verbose = x;
        }
        else if (buf[0] == '/' && buf[1] == '/')
        {
            fgets(buf, sizeof(buf), fp);
        }
        else if (strcmp(buf, "END") == 0 || isNumber(buf))
        {
            break;
        }
        else
        {
            printf("Invalid section name \"%s\" in config file\n", buf);
            exit(-1);
        }
    }
    fclose(fp);
}

void prepareNpcBStat(const NonPlayer& npc, BStat& b)
{
    switch (npc.role)
    {
    case ROLE_MU:
        b.pAtkB = npc.lvl * 12.0;
        b.mAtkB = npc.lvl * 2.0;
        b.spdB = npc.lvl * 2.5;
        b.pBrcP = 30.0;
        b.pBrcA = npc.lvl * 1.0;
        b.mBrcP = 0.0;
        b.mBrcA = 0.0;
        b.cBrcP = 10.0;
        b.pDefB = npc.lvl * 2.5;
        b.mDefB = npc.lvl * 3.0;
        b.hpM = npc.lvl * 200.0;
        b.hpRecP = 5.0;
        b.sldM = npc.lvl * 30.0;
        b.sldRecP = 0.0;
        b.lchP = 0.0;
        b.rflP = 0.0;
        b.pRdc = 0.0;
        b.mRdc = 0.0;
        b.sRateB = npc.lvl * sklRate[npc.role][0] / sklRate[npc.role][1];
        b.cRateB = npc.lvl * crtRate[npc.role][0] / crtRate[npc.role][1];
        b.defLvl = b.atkLvl = 0;
        b.tAgi = npc.lvl * 1.0;
        b.psvSkl = npc.prefix * 5 + npc.prefixCount;
        break;
    case ROLE_ZHU:
        b.pAtkB = npc.lvl * 2.0;
        b.mAtkB = npc.lvl * 8.0;
        b.spdB = npc.lvl * 8.0;
        b.pBrcP = 0.0;
        b.pBrcA = 0.0;
        b.mBrcP = 50.0;
        b.mBrcA = npc.lvl * 1.0;
        b.cBrcP = 10.0;
        b.pDefB = npc.lvl * 1.0;
        b.mDefB = npc.lvl * 1.0;
        b.hpM = npc.lvl * 50.0;
        b.hpRecP = 0.0;
        b.sldM = 0.0;
        b.sldRecP = 0.0;
        b.lchP = 50.0;
        b.rflP = 0.0;
        b.pRdc = 0.0;
        b.mRdc = 0.0;
        b.sRateB = npc.lvl * sklRate[npc.role][0] / sklRate[npc.role][1];
        b.cRateB = npc.lvl * crtRate[npc.role][0] / crtRate[npc.role][1];
        b.defLvl = b.atkLvl = 0;
        b.tAgi = npc.lvl * 1.0;
        b.psvSkl = npc.prefix * 5 + npc.prefixCount;
        break;
    case ROLE_DENG:
        b.pAtkB = 1.0;
        b.mAtkB = 1.0;
        b.spdB = npc.lvl * 2.7;
        b.pBrcP = 0.0;
        b.pBrcA = 0.0;
        b.mBrcP = 30.0;
        b.mBrcA = npc.lvl * 1.0;
        b.cBrcP = 0.0;
        b.pDefB = npc.lvl * 1.0;
        b.mDefB = npc.lvl * 1.0;
        b.hpM = 1.0;
        b.hpRecP = 0.0;
        b.sldM = npc.lvl * 500.0;
        b.sldRecP = 5.0;
        b.lchP = 0.0;
        b.rflP = 0.0;
        b.pRdc = 0.0;
        b.mRdc = 0.0;
        b.sRateB = npc.lvl * sklRate[npc.role][0] / sklRate[npc.role][1];
        b.cRateB = npc.lvl * crtRate[npc.role][0] / crtRate[npc.role][1];
        b.defLvl = b.atkLvl = 0;
        b.tAgi = npc.lvl * 1.0;
        b.psvSkl = npc.prefix * 5 + npc.prefixCount;
        break;
    case ROLE_SHOU:
        b.pAtkB = npc.lvl * 33.0;
        b.mAtkB = 1.0;
        b.spdB = npc.lvl * 1.0;
        b.pBrcP = 20.0;
        b.pBrcA = npc.lvl * 3.0;
        b.mBrcP = 0.0;
        b.mBrcA = 0.0;
        b.cBrcP = 20.0;
        b.pDefB = npc.lvl * 5.0;
        b.mDefB = npc.lvl * 3.0;
        b.hpM = npc.lvl * 300.0;
        b.hpRecP = 5.0;
        b.sldM = 0.0;
        b.sldRecP = 0.0;
        b.lchP = 0.0;
        b.rflP = 40.0;
        b.pRdc = 0.0;
        b.mRdc = 0.0;
        b.sRateB = npc.lvl * sklRate[npc.role][0] / sklRate[npc.role][1];
        b.cRateB = npc.lvl * crtRate[npc.role][0] / crtRate[npc.role][1];
        b.defLvl = b.atkLvl = 0;
        b.tAgi = npc.lvl * 1.0;
        b.psvSkl = npc.prefix * 5 + npc.prefixCount;
        break;
    case ROLE_MU2:
        b.pAtkB = npc.lvl * 30.0;
        b.mAtkB = npc.lvl * 30.0;
        b.spdB = npc.lvl * 3.0;
        b.pBrcP = 50.0;
        b.pBrcA = npc.lvl * 2.0;
        b.mBrcP = 50.0;
        b.mBrcA = npc.lvl * 2.0;
        b.cBrcP = 0.0;
        b.pDefB = npc.lvl * 5.0;
        b.mDefB = npc.lvl * 5.0;
        b.hpM = npc.lvl * 600.0;
        b.hpRecP = 0.0;
        b.sldM = npc.lvl * 600.0;
        b.sldRecP = 0.0;
        b.lchP = 0.0;
        b.rflP = 0.0;
        b.pRdc = 0.0;
        b.mRdc = 0.0;
        b.sRateB = npc.lvl * sklRate[npc.role][0] / sklRate[npc.role][1];
        b.cRateB = npc.lvl * crtRate[npc.role][0] / crtRate[npc.role][1];
        b.defLvl = b.atkLvl = 0;
        b.tAgi = npc.lvl * 1.0;
        b.psvSkl = (AURA_SHANG | AURA_SHEN | AURA_REN | AURA_WU | AURA_DI);
        break;
    case ROLE_ZHU2:
        b.pAtkB = 0.0;
        b.mAtkB = npc.lvl * 40.0;
        b.spdB = npc.lvl * 9.0;
        b.pBrcP = 0.0;
        b.pBrcA = 0.0;
        b.mBrcP = 50.0;
        b.mBrcA = npc.lvl * 3.0;
        b.cBrcP = 0.0;
        b.pDefB = npc.lvl * 4.0;
        b.mDefB = npc.lvl * 4.0;
        b.hpM = npc.lvl * 10.0;
        b.hpRecP = 0.0;
        b.sldM = npc.lvl * 400.0;
        b.sldRecP = 0.0;
        b.lchP = 0.0;
        b.rflP = 0.0;
        b.pRdc = 0.0;
        b.mRdc = 0.0;
        b.sRateB = npc.lvl * sklRate[npc.role][0] / sklRate[npc.role][1];
        b.cRateB = npc.lvl * crtRate[npc.role][0] / crtRate[npc.role][1];
        b.defLvl = b.atkLvl = 0;
        b.tAgi = npc.lvl * 1.0;
        b.psvSkl = (AURA_XIAO | AURA_SHANG | AURA_SHEN | AURA_RE | AURA_WU | AURA_DI);
        break;
    case ROLE_DENG2:
        b.pAtkB = 1.0;
        b.mAtkB = 1.0;
        b.spdB = npc.lvl * 3.0;
        b.pBrcP = 0.0;
        b.pBrcA = 0.0;
        b.mBrcP = 50.0;
        b.mBrcA = npc.lvl * 3.0;
        b.cBrcP = 0.0;
        b.pDefB = npc.lvl * 5.0;
        b.mDefB = npc.lvl * 5.0;
        b.hpM = 1.0;
        b.hpRecP = 0.0;
        b.sldM = npc.lvl * 900.0;
        b.sldRecP = 0.0;
        b.lchP = 0.0;
        b.rflP = 0.0;
        b.pRdc = 0.0;
        b.mRdc = 0.0;
        b.sRateB = npc.lvl * sklRate[npc.role][0] / sklRate[npc.role][1];
        b.cRateB = npc.lvl * crtRate[npc.role][0] / crtRate[npc.role][1];
        b.defLvl = b.atkLvl = 0;
        b.tAgi = npc.lvl * 1.0;
        b.psvSkl = (AURA_DUN | AURA_SHANG | AURA_SHEN | AURA_REN | AURA_DI);
        break;
    case ROLE_SHOU2:
        b.pAtkB = npc.lvl * 80.0;
        b.mAtkB = 1.0;
        b.spdB = npc.lvl * 1.0;
        b.pBrcP = 50.0;
        b.pBrcA = npc.lvl * 3.0;
        b.mBrcP = 0.0;
        b.mBrcA = 0.0;
        b.cBrcP = 30.0;
        b.pDefB = npc.lvl * 8.0;
        b.mDefB = npc.lvl * 8.0;
        b.hpM = npc.lvl * 600.0;
        b.hpRecP = 0.0;
        b.sldM = 0.0;
        b.sldRecP = 0.0;
        b.lchP = 0.0;
        b.rflP = 30.0;
        b.pRdc = 0.0;
        b.mRdc = 0.0;
        b.sRateB = npc.lvl * sklRate[npc.role][0] / sklRate[npc.role][1];
        b.cRateB = npc.lvl * crtRate[npc.role][0] / crtRate[npc.role][1];
        b.defLvl = b.atkLvl = 0;
        b.tAgi = npc.lvl * 1.0;
        b.psvSkl = (AURA_SHANG | AURA_SHEN | AURA_CI | AURA_REN | AURA_DI);
        break;
    case ROLE_YU2:
        b.pAtkB = npc.lvl * 30.0;
        b.mAtkB = 0.0;
        b.spdB = npc.lvl * 8.0;
        b.pBrcP = 80.0;
        b.pBrcA = npc.lvl * 2.0;
        b.mBrcP = 0.0;
        b.mBrcA = 0.0;
        b.cBrcP = 0.0;
        b.pDefB = npc.lvl * 4.0;
        b.mDefB = npc.lvl * 4.0;
        b.hpM = npc.lvl * 400.0;
        b.hpRecP = 0.0;
        b.sldM = 0.0;
        b.sldRecP = 0.0;
        b.lchP = 0.0;
        b.rflP = 0.0;
        b.pRdc = 0.0;
        b.mRdc = 0.0;
        b.sRateB = npc.lvl * sklRate[npc.role][0] / sklRate[npc.role][1];
        b.cRateB = npc.lvl * crtRate[npc.role][0] / crtRate[npc.role][1];
        b.defLvl = b.atkLvl = 0;
        b.tAgi = npc.lvl * 1.0;
        b.psvSkl = (AURA_XIAO | AURA_SHANG | AURA_SHEN | AURA_RE | AURA_WU | AURA_DI);
        break;
    case ROLE_HAO2:
        b.pAtkB = npc.lvl * 30.0;
        b.mAtkB = 1.0;
        b.spdB = npc.lvl * 1.0;
        b.pBrcP = 50.0;
        b.pBrcA = npc.lvl * 2.0;
        b.mBrcP = 50.0;
        b.mBrcA = npc.lvl * 2.0;
        b.cBrcP = 0.0;
        b.pDefB = npc.lvl * 6.0;
        b.mDefB = npc.lvl * 6.0;
        b.hpM = npc.lvl * 900.0;
        b.hpRecP = 0.0;
        b.sldM = 0.0;
        b.sldRecP = 0.0;
        b.lchP = 0.0;
        b.rflP = 80.0;
        b.pRdc = 0.0;
        b.mRdc = 0.0;
        b.sRateB = npc.lvl * sklRate[npc.role][0] / sklRate[npc.role][1];
        b.cRateB = npc.lvl * crtRate[npc.role][0] / crtRate[npc.role][1];
        b.defLvl = b.atkLvl = 0;
        b.tAgi = npc.lvl * 1.0;
        b.psvSkl = (AURA_SHENG | AURA_SHANG | AURA_SHEN | AURA_CI | AURA_DI);
        break;
    case ROLE_LIU:
        // Init base status later
        b.pAtkB = b.mAtkB = b.spdB = 0.0;
        b.pBrcP = b.pBrcA = b.mBrcP = b.mBrcA = b.cBrcP = 0.0;
        b.pDefB = b.mDefB = b.hpM = b.hpRecP = b.sldM = b.sldRecP = 0.0;
        b.lchP = b.rflP = b.sRateB = b.cRateB = 0.0;
        b.pRdc = b.mRdc = 0.0;
        b.defLvl = b.atkLvl = 0;
        b.tAgi = npc.lvl * 1.0;
        b.psvSkl = npc.prefix;
        break;
    case ROLE_SHI:
        b.pAtkB = npc.lvl * 60.0;
        b.mAtkB = npc.lvl * 60.0;
        b.aAtk = npc.lvl * 10.0;
        b.spdB = npc.lvl * 5.0;
        b.pBrcP = 0.0; // not sure
        b.pBrcA = npc.lvl * 3.0; // not sure
        b.mBrcP = 0.0; // not sure
        b.mBrcA = npc.lvl * 3.0; // not sure
        b.cBrcP = 0.0;
        b.pDefB = npc.lvl * 3.0;
        b.mDefB = npc.lvl * 3.0;
        b.hpM = npc.lvl * 300.0;
        b.hpRecP = 4.0;
        b.sldM = npc.lvl * 400.0;
        b.sldRecP = 6.0;
        b.lchP = 10.0;
        b.rflP = 10.0;
        b.pRdc = npc.lvl * 10.0;
        b.mRdc = npc.lvl * 10.0;
        b.sRateB = npc.lvl * sklRate[npc.role][0] / sklRate[npc.role][1];
        b.cRateB = npc.lvl * crtRate[npc.role][0] / crtRate[npc.role][1];
        b.defLvl = b.atkLvl = 0;
        b.tAgi = npc.lvl * 1.0;
        b.psvSkl = (AURA_DUN | AURA_SHENG | AURA_SHANG | AURA_SHEN | AURA_REN | AURA_RE | AURA_WU | AURA_DI);
        break;
    }

    b.role = npc.role;
    b.lvl = npc.lvl;
    b.hp = b.hpM;
    b.hpRecA = 0.0;
    b.hpRecRR = 0.0;
    b.pAtkA = 0.0;
    b.mAtkA = 0.0;
    b.spdA = 0.0;
    b.spdRR = 0.0;
    b.spdC = b.spdB * (1 - b.spdRR / 100);
    b.sRateP = b.sRateB * 100 / (b.sRateB + 99);
    b.cRateP = b.cRateB * 100 / (b.cRateB + 99);
    b.pDefA = 0.0;
    b.mDefA = 0.0;
    b.sld = b.sldM;
    b.sldRecA = 0.0;
    b.sldRecRR = 0.0;
    b.myst = 0;
    b.sklC = 0;
    b.houC = 0;
    for (int i = 0; i < WISH_COUNT; ++i)
    {
        b.wish[i] = 0;
    }
    for (int i = 0; i < AMUL_COUNT; ++i)
    {
        b.amul[i] = 0;
    }
}

void prepareLiuStat(BStat& b, int* rseed)
{
    int cat = b.psvSkl;
    b.psvSkl = 0;
    int v = 0;

    // Cat0: Atk
    v = (cat & 3);
    if (v == 3) v = myrand(rseed, 3);
    int pAtkCoef = (cat >> 24 & 7);
    pAtkCoef = (pAtkCoef == 7 ? myrand(rseed, 5) : pAtkCoef) + 28;
    int mAtkCoef = (cat >> 27 & 7);
    mAtkCoef = (mAtkCoef == 7 ? myrand(rseed, 5) : mAtkCoef) + 28;
    switch (v)
    {
    case 0:
        b.pAtkB = b.lvl * pAtkCoef * 3.0;
        b.mAtkB = (b.lvl * mAtkCoef + 9) / 10;
        b.psvSkl |= AURA_FEI;
        break;
    case 1:
        b.pAtkB = (b.lvl * pAtkCoef + 9) / 10;
        b.mAtkB = b.lvl * mAtkCoef * 3.0;
        b.psvSkl |= AURA_BO;
        break;
    case 2:
        b.pAtkB = (b.lvl * pAtkCoef + 9) / 10;
        b.mAtkB = b.lvl * mAtkCoef * 3.0;
        b.psvSkl |= AURA_FEI | AURA_BO;
        break;
    }

    // Cat1: Brc, SklRate, CrtRate
    v = (cat >> 2 & 3);
    if (v == 3) v = myrand(rseed, 3);
    switch (v)
    {
    case 0:
        b.pBrcP = b.mBrcP = 20.0; // Unknown <40
        b.pBrcA = b.mBrcA = b.lvl * 2.0;
        b.sRateB = b.lvl * 4.0;
        b.cRateB = b.lvl * 1.0;
        b.psvSkl |= AURA_HONG;
        break;
    case 1:
        b.pBrcP = b.mBrcP = 20.0; // Unknown <40
        b.pBrcA = b.mBrcA = b.lvl * 2.0;
        b.sRateB = b.lvl * 1.0;
        b.cRateB = b.lvl * 4.0;
        b.psvSkl |= AURA_HONG;
        break;
    case 2:
        b.pBrcP = b.mBrcP = 70.0; // Not sure
        b.pBrcA = b.mBrcA = b.lvl * 2.0;
        b.cBrcP = 30.0;
        b.sRateB = b.lvl * 1.0;
        b.cRateB = b.lvl * 1.0;
        b.psvSkl |= AURA_BI | AURA_MO;
        break;
    }

    // Cat2: Spd, Lch
    v = (cat >> 4 & 3);
    if (v == 3) v = myrand(rseed, 3);
    switch (v)
    {
    case 0:
        b.spdB = b.lvl * 6.0;
        b.lchP = 10.0;
        b.psvSkl |= AURA_XIAO | AURA_RE | AURA_JU;
        break;
    case 1:
        b.spdB = b.lvl * 1.0;
        b.lchP = 60.0;
        b.psvSkl |= AURA_HOU;
        break;
    case 2:
        b.spdB = b.lvl * 1.0;
        b.lchP = 10.0;
        b.aAtk = (b.pAtkB + 4) / 5 + (b.mAtkB + 4) / 5;
        break;
    }

    // Cat3: Hp, Sld
    v = (cat >> 6 & 3);
    if (v == 3) v = myrand(rseed, 3);
    int hpCoef = (cat >> 12 & 63);
    hpCoef = (hpCoef == 63 ? myrand(rseed, 41) : hpCoef) + 280;
    int sldCoef = (cat >> 18 & 63);
    sldCoef = (sldCoef == 63 ? myrand(rseed, 41) : sldCoef) + 280;
    switch (v)
    {
    case 0:
        b.hp = b.hpM = b.lvl * hpCoef * 1.0;
        b.sld = b.sldM = b.lvl * sldCoef * 1.0;
        b.hpRecP = b.sldRecP = 10.0;
        b.psvSkl |= AURA_DIAN;
        break;
    case 1:
        b.hp = b.hpM = b.lvl * hpCoef * 3.0;
        b.sld = b.sldM = (b.lvl * sldCoef + 9) / 10;
        b.hpRecP = b.sldRecP = 0.0;
        b.psvSkl |= AURA_SHENG | AURA_REN;
        break;
    case 2:
        b.hp = b.hpM = (b.lvl * hpCoef + 9) / 10;
        b.sld = b.sldM = b.lvl * sldCoef * 6.0;
        b.hpRecP = b.sldRecP = 0.0;
        b.psvSkl |= AURA_DUN | AURA_ZHI;
        break;
    }

    // Cat4: Def, Rfl
    v = (cat >> 8 & 3);
    if (v == 3) v = myrand(rseed, 3);
    switch (v)
    {
    case 0:
        b.pDefB = b.lvl * 6.0;
        b.mDefB = b.lvl * 2.0;
        b.rflP = 10.0;
        break;
    case 1:
        b.pDefB = b.lvl * 2.0;
        b.mDefB = b.lvl * 6.0;
        b.rflP = 10.0;
        break;
    case 2:
        b.pDefB = b.lvl * 2.0;
        b.mDefB = b.lvl * 2.0;
        b.rflP = 40.0;
        b.psvSkl |= AURA_CI;
        break;
    }

    // Cat5: Other
    v = (cat >> 10 & 3);
    if (v == 3) v = myrand(rseed, 3);
    switch (v)
    {
    case 0:
        b.psvSkl |= AURA_SHANG | AURA_SHEN;
        break;
    case 1:
        b.psvSkl |= AURA_DUNH | AURA_WU;
        break;
    case 2:
        b.psvSkl |= AURA_JUE | AURA_E;
        break;
    }
}

void preparePcBStat(const Player& pc, BStat& b)
{
    if (pc.pBStat)
    {
        b = *pc.pBStat;
        return;
    }

    b.mode = pc.mode;

    b.atkLvl = pc.kfLvl > 1500 ? 15 : pc.kfLvl / 100;
    b.defLvl = pc.kfLvl > 1500 ? 15 : pc.kfLvl / 100;

    b.tStr = pc.attr[ATTR_STR];
    b.tAgi = pc.attr[ATTR_AGI];
    b.tInt = pc.attr[ATTR_INT];
    b.tVit = pc.attr[ATTR_VIT];
    b.tSpr = pc.attr[ATTR_SPR];
    b.tMnd = pc.attr[ATTR_MND];

    int tStr = pc.attr[ATTR_STR] + pc.amul[AMUL_STR] + pc.amul[AMUL_AAA];
    int tAgi = pc.attr[ATTR_AGI] + pc.amul[AMUL_AGI] + pc.amul[AMUL_AAA];
    int tInt = pc.attr[ATTR_INT] + pc.amul[AMUL_INT] + pc.amul[AMUL_AAA];
    int tVit = pc.attr[ATTR_VIT] + pc.amul[AMUL_VIT] + pc.amul[AMUL_AAA];
    int tSpr = pc.attr[ATTR_SPR] + pc.amul[AMUL_SPR] + pc.amul[AMUL_AAA];
    int tMnd = pc.attr[ATTR_MND] + pc.amul[AMUL_MND] + pc.amul[AMUL_AAA];
    int vitMnd = tVit + tMnd;
    bool allAttrBool = pc.kfLvl >= 1500 && tStr >= 450 && tAgi >= 450 && tInt >= 450 && tVit >= 450 && tSpr >= 450 && tMnd >= 450;
    b.role = pc.role;
    b.lvl = pc.lvl;
    b.hpM = (vitMnd * (35.0 +
        (pc.kfLvl >= 300 && vitMnd >= 200 ? 7.0 : 0.0) +
        (pc.kfLvl >= 600 && vitMnd >= 500 ? 10.0 : 0.0) +
        (pc.kfLvl >= 800 && vitMnd >= 1000 ? 17.0 : 0.0))) + (tStr *
        (pc.kfLvl >= 1300 && tStr > tAgi + tInt + tVit + tSpr + tMnd ? 30.0 : 0.0));
    b.hpRecP = (pc.kfLvl >= 200 && tStr >= 200 ? 2.0 : 0.0) +
        (pc.kfLvl >= 500 && tStr >= 500 ? 3.0 : 0.0);
    b.hpRecA = 0.0;
    b.hpRecRR = 0.0;
    b.cDef = 0.0;
    b.sDef = 0.0;
    b.pAtkB = tStr * (10.0 +
        (pc.kfLvl >= 50 ? 3.0 : 0.0) +
        (pc.kfLvl >= 200 && tStr >= 200 ? 4.0 : 0.0) +
        (pc.kfLvl >= 500 && tStr >= 500 ? 6.0 : 0.0) +
        (pc.kfLvl >= 700 && tStr >= 800 ? 10.0 : 0.0) +
        (pc.kfLvl >= 1200 && tAgi > tStr + tInt ? 10.0 : 0.0));
    b.pAtkA = pc.wish[WISH_PATKA] * 5.0;
    b.mAtkB = tInt * (10.0 +
        (pc.kfLvl >= 200 && tInt >= 200 ? 4.0 : 0.0) +
        (pc.kfLvl >= 500 && tInt >= 500 ? 6.0 : 0.0) +
        (pc.kfLvl >= 700 && tInt >= 800 ? 10.0 : 0.0) +
        (pc.kfLvl >= 1200 && tAgi > tStr + tInt ? 10.0 : 0.0));
    b.mAtkA = pc.wish[WISH_MATKA] * 5.0;
    b.aAtk = 0.0;
    b.spdB = tAgi * 3;
    b.spdA = tAgi * ((pc.kfLvl >= 1000 && tAgi >= 1000 ? 0.5 : 0.0) +
        (allAttrBool ? 1.0 : 0.0)) + pc.wish[WISH_SPDA];
    b.pBrcP = (pc.kfLvl >= 900 && tStr >= 1500 ? 20.0 : 0.0);
    b.pBrcA = tStr * ((pc.kfLvl >= 100 ? 1.0 : 0.0) +
        (allAttrBool ? 1.0 : 0.0)) + pc.wish[WISH_PBRCA];
    b.mBrcP = (pc.kfLvl >= 900 && tInt >= 1500 ? 20.0 : 0.0);
    b.mBrcA = tInt * ((pc.kfLvl >= 100 ? 1.0 : 0.0) +
        (allAttrBool ? 1.0 : 0.0)) + pc.wish[WISH_MBRCA];
    b.sRateB = tInt + (pc.kfLvl >= 50 ? tStr / 2.0 : 0.0);
    b.cRateB = tAgi + (pc.kfLvl >= 1000 && tAgi >= 1000 ? tAgi / 10.0 : 0.0);
    b.cBrcP = 0.0;
    b.lchP = 0.0;
    b.pDefB = tVit * (1.0 +
        (pc.kfLvl >= 400 ? 1.0 : 0.0) +
        (pc.kfLvl >= 900 && vitMnd >= 1500 ? 2.0 : 0.0) +
        (allAttrBool ? 2.0 : 0.0)) +
        tSpr / 2 * (1 +
            (pc.kfLvl >= 400 ? 1.0 : 0.0) +
            (pc.kfLvl >= 1100 ? 1.0 : 0.0) +
            (allAttrBool ? 2.0 : 0.0));
    b.pDefA = pc.wish[WISH_PDEFA] * 1.0;
    b.mDefB = tMnd * (1.0 +
        (pc.kfLvl >= 400 ? 1.0 : 0.0) +
        (pc.kfLvl >= 900 && vitMnd >= 1500 ? 2.0 : 0.0) +
        (allAttrBool ? 2.0 : 0.0)) +
        tSpr / 2.0 * (1.0 +
            (pc.kfLvl >= 400 ? 1.0 : 0.0) +
            (pc.kfLvl >= 1100 ? 1.0 : 0.0) +
            (allAttrBool ? 2.0 : 0.0));
    b.mDefA = pc.wish[WISH_MDEFA] * 1.0;
    b.pRdc = 0.0;
    b.mRdc = 0.0;
    b.sldM = (tSpr * (65.0 +
        (pc.kfLvl >= 300 && tSpr >= 200 ? 13.0 : 0.0) +
        (pc.kfLvl >= 600 && tSpr >= 500 ? 21.0 : 0.0) +
        (pc.kfLvl >= 800 && tSpr >= 1000 ? 32.0 : 0.0))) + (tInt *
        (pc.kfLvl >= 1400 && tInt > tStr + tAgi + tVit + tSpr + tMnd ? 45.0 : 0.0));
    b.sldRecP = (pc.kfLvl >= 200 && tInt >= 200 ? 2.0 : 0.0) +
        (pc.kfLvl >= 500 && tInt >= 500 ? 3.0 : 0.0);
    b.sldRecA = 0.0;
    b.sldRecRR = 0.0;
    b.rflP = 0.0;
    b.psvSkl = pc.auraSkl;
    b.myst = 0;
    b.sklC = (b.role == ROLE_MIN ? 1 : b.role == ROLE_WU ? (pc.growth > 106800 ? 106800 : pc.growth) : 0);
    b.houC = 0;
    for (int i = 0; i < WISH_COUNT; ++i)
    {
        b.wish[i] = pc.wish[i];
    }
    for (int i = 0; i < AMUL_COUNT; ++i)
    {
        b.amul[i] = pc.amul[i];
    }

    double hpPlus = 0.0;
    double hpAdd = pc.wish[WISH_HPM] * 12.0;
    double pAtkPlus = 0.0;
    double mAtkPlus = 0.0;
    double spdPlus = 0.0;
    double sldPlus = 0.0;
    double sldAdd = pc.wish[WISH_SLDM] * 20.0;
    for (int i = 0; i < 4; ++i)
    {
        const Gear& g = pc.gear[i];
        switch (g.type)
        {
        case GEAR_SWORD:
            b.pAtkA += int(g.lvl * 10 * (g.percent[0] / 10.0)) / 10.0;
            b.mAtkA += int(g.lvl * 10 * (g.percent[1] / 10.0)) / 10.0;
            b.pBrcA += int(g.lvl * (g.percent[2] / 10.0)) / 10.0;
            b.lchP += int((g.lvl / 15.0 + 10) * (g.percent[3] / 10.0)) / 10.0;
            break;
        case GEAR_BOW:
            b.pAtkA += int(g.lvl * 10 * (g.percent[0] / 10.0)) / 10.0;
            b.mAtkA += int(g.lvl * 10 * (g.percent[1] / 10.0)) / 10.0;
            b.spdA += int(g.lvl * 2 * (g.percent[2] / 10.0)) / 10.0;
            b.lchP += int((g.lvl / 15.0 + 10) * (g.percent[3] / 10.0)) / 10.0;
            break;
        case GEAR_STAFF:
            b.pAtkA += int(g.lvl * 10 * (g.percent[0] / 10.0)) / 10.0;
            b.mAtkA += int(g.lvl * 10 * (g.percent[1] / 10.0)) / 10.0;
            b.mBrcP += int((g.lvl / 20.0 + 5) * (g.percent[2] / 10.0)) / 10.0;
            b.lchP += int((g.lvl / 15.0 + 10) * (g.percent[3] / 10.0)) / 10.0;
            break;
        case GEAR_BLADE:
            pAtkPlus += round(b.pAtkB * (int((g.lvl / 5.0 + 20) * (g.percent[0] / 10.0)) / 1000.0) * 100.0) / 100.0;
            spdPlus += round(b.spdB * (int((g.lvl / 5.0 + 20) * (g.percent[1] / 10.0)) / 1000.0) * 100.0) / 100.0;
            b.cBrcP += int((g.lvl / 20.0 + 10) * (g.percent[2] / 10.0)) / 10.0;
            b.pBrcP += int((g.lvl / 20.0 + 10) * (g.percent[3] / 10.0)) / 10.0;
            if (g.isMyst) b.myst |= MYST_BLADE;
            break;
        case GEAR_ASSBOW:
            pAtkPlus += round(b.pAtkB * (int((g.lvl / 5.0 + 30) * (g.percent[0] / 10.0)) / 1000.0) * 100.0) / 100.0;
            b.cBrcP += int((g.lvl / 20.0 + 10) * (g.percent[1] / 10.0)) / 10.0;
            b.pBrcP += int((g.lvl / 20.0 + 10) * (g.percent[2] / 10.0)) / 10.0;
            b.pBrcA += int(g.lvl * (g.percent[3] / 10.0)) / 10.0;
            if (g.isMyst) b.myst |= MYST_ASSBOW;
            break;
        case GEAR_DAGGER:
            pAtkPlus += round(b.pAtkB * (int(g.lvl / 5.0 * (g.percent[0] / 10.0)) / 1000.0) * 100.0) / 100.0;
            mAtkPlus += round(b.mAtkB * (int(g.lvl / 5.0 * (g.percent[1] / 10.0)) / 1000.0) * 100.0) / 100.0;
            b.spdA += int(g.lvl * 4 * (g.percent[2] / 10.0)) / 10.0;
            spdPlus += int(b.spdB * (int((g.lvl / 5.0 + 25) * (g.percent[3] / 10.0)) / 1000.0) * 10.0) / 10.0;
            if (g.isMyst) b.myst |= MYST_DAGGER;
            break;
        case GEAR_WAND:
            mAtkPlus += round(b.mAtkB * (int(g.lvl / 5.0 * (g.percent[0] / 10.0)) / 1000.0) * 100.0) / 100.0;
            mAtkPlus += round(b.mAtkB * (int(g.lvl / 5.0 * (g.percent[1] / 10.0)) / 1000.0) * 100.0) / 100.0;
            mAtkPlus += round(b.mAtkB * (int(g.lvl / 5.0 * (g.percent[2] / 10.0)) / 1000.0) * 100.0) / 100.0;
            b.mBrcP += int(g.lvl / 20.0 * (g.percent[3] / 10.0)) / 10.0;
            if (g.isMyst) b.myst |= MYST_WAND;
            break;
        case GEAR_SHIELD:
            b.lchP += int((g.lvl / 15.0 + 10) * (g.percent[0] / 10.0)) / 10.0;
            b.rflP += int(g.lvl / 15.0 * (g.percent[1] / 10.0)) / 10.0;
            b.pDefA += int(g.lvl * (g.percent[2] / 10.0)) / 10.0;
            b.mDefA += int(g.lvl * (g.percent[3] / 10.0)) / 10.0;
            if (g.isMyst) b.myst |= MYST_SHIELD;
            break;
        case GEAR_CLAYMORE:
            b.pAtkA += int(g.lvl * 20 * (g.percent[0] / 10.0)) / 10.0;
            b.pAtkA += int(g.lvl * 20 * (g.percent[1] / 10.0)) / 10.0;
            pAtkPlus += round(b.pAtkB * (int((g.lvl / 5.0 + 30) * (g.percent[2] / 10.0)) / 1000.0) * 100.0) / 100.0;
            b.cBrcP += int((g.lvl / 20.0 + 1) * (g.percent[3] / 10.0)) / 10.0;
            if (g.isMyst) b.myst |= MYST_CLAYMORE;
            break;
        case GEAR_SPEAR:
            pAtkPlus += round(b.pAtkB * (int((g.lvl / 5.0 + 50) * (g.percent[0] / 10.0)) / 1000.0) * 100.0) / 100.0;
            b.pBrcP += int((g.lvl / 20.0 + 10) * (g.percent[1] / 10.0)) / 10.0;
            b.mBrcA += int(g.lvl * 2 * (g.percent[2] / 10.0)) / 10.0;
            b.lchP += int((g.lvl / 15.0 + 10) * (g.percent[3] / 10.0)) / 10.0;
            if (g.isMyst) b.myst |= MYST_SPEAR;
            break;
        case GEAR_COLORFUL:
            pAtkPlus += round(b.pAtkB * (int((g.lvl / 5.0 + 10) * (g.percent[0] / 10.0)) / 1000.0) * 100.0) / 100.0;
            mAtkPlus += round(b.mAtkB * (int((g.lvl / 5.0 + 10) * (g.percent[1] / 10.0)) / 1000.0) * 100.0) / 100.0;
            spdPlus += round(b.spdB * (int((g.lvl / 5.0 + 20) * (g.percent[2] / 10.0)) / 1000.0) * 100.0) / 100.0;
            b.aAtk += tAgi * int(g.lvl * 0.04 * (g.percent[3] / 10.0)) / 10.0;
            if (g.isMyst) b.myst |= MYST_COLORFUL;
            break;
        case GEAR_LIMPIDWAND:
            mAtkPlus += round(b.mAtkB * (int((g.lvl / 5.0 + 20) * (g.percent[0] / 10.0)) / 1000.0) * 100.0) / 100.0;
            b.mBrcP += int((g.lvl / 20.0 + 5) * (g.percent[1] / 10.0)) / 10.0;
            spdPlus += round(b.spdB * (int((g.lvl / 5.0) * (g.percent[2] / 10.0)) / 1000.0) * 100.0) / 100.0;
            b.spdA += tInt * int(g.lvl / 375.0 * (g.percent[3] / 10.0)) / 10.0;
            if (g.isMyst) b.myst |= MYST_LIMPIDWAND;
            break;
        case GEAR_GLOVES:
            b.pAtkA += int(g.lvl * 10 * (g.percent[0] / 10.0)) / 10.0;
            b.mAtkA += int(g.lvl * 10 * (g.percent[1] / 10.0)) / 10.0;
            b.spdA += int(g.lvl * 2 * (g.percent[2] / 10.0)) / 10.0;
            hpAdd += int(g.lvl * 10 * (g.percent[3] / 10.0)) / 10.0;
            break;
        case GEAR_BRACELET:
            mAtkPlus += round(b.mAtkB * (int((g.lvl / 5.0 + 1) * (g.percent[0] / 10.0)) / 1000.0) * 100.0) / 100.0;
            b.mBrcP += int((g.lvl / 20.0 + 1) * (g.percent[1] / 10.0)) / 10.0;
            sldAdd += int(g.lvl * 20 * (g.percent[2] / 10.0)) / 10.0;
            b.mDefA += int(g.lvl * (g.percent[3] / 10.0)) / 10.0;
            if (g.isMyst) b.myst |= MYST_BRACELET;
            break;
        case GEAR_VULTURE:
            b.lchP += int((g.lvl / 15.0 + 1) * (g.percent[0] / 10.0)) / 10.0;
            b.lchP += int((g.lvl / 15.0 + 1) * (g.percent[1] / 10.0)) / 10.0;
            b.lchP += int((g.lvl / 15.0 + 1) * (g.percent[2] / 10.0)) / 10.0;
            b.spdA += int(g.lvl * 2 * (g.percent[3] / 10.0)) / 10.0;
            if (g.isMyst) b.myst |= MYST_VULTURE;
            break;
        case GEAR_RING:
            b.pBrcA += int(g.lvl * 0.5 * (g.percent[0] / 10.0)) / 10.0;
            b.mBrcA += int(g.lvl * 0.5 * (g.percent[1] / 10.0)) / 10.0;
            b.cRateB += int(g.lvl * 0.8 * (g.percent[2] / 10.0)) / 10.0;
            b.sRateB += int(g.lvl * 0.8 * (g.percent[3] / 10.0)) / 10.0;
            if (g.isMyst) b.myst |= MYST_RING;
            break;
        case GEAR_DEVOUR:
            b.mBrcA += int(g.lvl * 0.5 * (g.percent[0] / 10.0)) / 10.0;
            b.sRateB += int(g.lvl * 0.8 * (g.percent[1] / 10.0)) / 10.0;
            hpAdd += tStr * (int(int(g.lvl * 0.08) * (g.percent[2] / 10.0)) / 10.0);
            hpPlus += round(b.hpM * (int(int(g.lvl * 0.07) * (g.percent[3] / 10.0)) / 1000.0) * 100.0) /100.0;
            if (g.isMyst) b.myst |= MYST_DEVOUR;
            break;
        case GEAR_PLATE:
            hpAdd += int(g.lvl * 20 * (g.percent[0] / 10.0)) / 10.0;
            b.pDefA += int(g.lvl * (g.percent[1] / 10.0)) / 10.0;
            b.mDefA += int(g.lvl * (g.percent[2] / 10.0)) / 10.0;
            b.hpRecA += int(g.lvl * 10 * (g.percent[3] / 10.0)) / 10.0;
            break;
        case GEAR_LEATHER:
        case GEAR_CLOTH:
            hpAdd += int(g.lvl * 25 * (g.percent[0] / 10.0)) / 10.0;
            b.pRdc += int(g.lvl * 2 * (g.percent[1] / 10.0)) / 10.0;
            b.mRdc += int(g.lvl * 2 * (g.percent[2] / 10.0)) / 10.0;
            b.hpRecA += int(g.lvl * 6 * (g.percent[3] / 10.0)) / 10.0;
            break;
        case GEAR_CLOAK:
            hpAdd += int(g.lvl * 10 * (g.percent[0] / 10.0)) / 10.0;
            b.sldRecA += int(g.lvl * 60 * (g.percent[1] / 10.0)) / 10.0;
            sldPlus += round(b.sldM * (int((g.lvl / 5.0 + 25) * (g.percent[2] / 10.0)) / 1000.0) * 100.0) / 100.0;
            sldAdd += int(g.lvl * 50 * (g.percent[3] / 10.0)) / 10.0;
            if (g.isMyst) b.myst |= MYST_CLOAK;
            break;
        case GEAR_THORN:
            hpPlus += round(b.hpM * (int((g.lvl / 5.0 + 20) * (g.percent[0] / 10.0)) / 1000.0) * 100.0) / 100.0;
            b.pDefA += int(g.lvl * (g.percent[1] / 10.0)) / 10.0;
            b.mDefA += int(g.lvl * (g.percent[2] / 10.0)) / 10.0;
            b.rflP += int((g.lvl / 15.0 + 10) * (g.percent[3] / 10.0)) / 10.0;
            if (g.isMyst) b.myst |= MYST_THORN;
            break;
        case GEAR_WOOD:
            hpPlus += round(b.hpM * (int((g.lvl / 5.0 + 50) * (g.percent[0] / 10.0)) / 1000.0) * 100.0) / 100.0;
            b.pRdc += int(g.lvl * 5 * (g.percent[1] / 10.0)) / 10.0;
            b.mRdc += int(g.lvl * 5 * (g.percent[2] / 10.0)) / 10.0;
            b.hpRecA += int(g.lvl * 20 * (g.percent[3] / 10.0)) / 10.0;
            if (g.isMyst) b.myst |= MYST_WOOD;
            break;
        case GEAR_CAPE:
            sldPlus += round(b.sldM * (int((g.lvl / 5.0 + 50) * (g.percent[0] / 10.0)) / 1000.0) * 100.0) / 100.0;
            sldAdd += int(g.lvl * 100 * (g.percent[1] / 10.0)) / 10.0;
            b.mDefA += int(g.lvl * (g.percent[2] / 10.0)) / 10.0;
            b.mRdc += int(g.lvl * 5 * (g.percent[3] / 10.0)) / 10.0;
            if (g.isMyst) b.myst |= MYST_CAPE;
            break;
        case GEAR_SCARF:
            hpAdd += int(g.lvl * 10 * (g.percent[0] / 10.0)) / 10.0;
            b.pRdc += int(g.lvl * 2 * (g.percent[1] / 10.0)) / 10.0;
            b.mRdc += int(g.lvl * 2 * (g.percent[2] / 10.0)) / 10.0;
            b.hpRecA += int(g.lvl * 4 * (g.percent[3] / 10.0)) / 10.0;
            break;
        case GEAR_TIARA:
            hpAdd += int(g.lvl * 5 * (g.percent[0] / 10.0)) / 10.0;
            sldPlus += round(b.sldM * (int(g.lvl / 5.0 * (g.percent[1] / 10.0)) / 1000.0) * 100.0) / 100.0;
            sldAdd += int(g.lvl * 20 * (g.percent[2] / 10.0)) / 10.0;
            b.pRdc += int(g.lvl * 2 * (g.percent[3] / 10.0)) / 10.0;
            if (g.isMyst) b.myst |= MYST_TIARA;
            break;
        case GEAR_RIBBON:
            b.pRdc += b.tVit * (int(g.lvl / 120.0 * (g.percent[0] / 10.0)) / 10.0);
            b.mRdc += b.tMnd * (int(g.lvl / 120.0 * (g.percent[1] / 10.0)) / 10.0);
            hpAdd += b.tVit * (int(g.lvl / 30.0 * (g.percent[2] / 10.0)) / 10.0);
            hpAdd += b.tMnd * (int(g.lvl / 30.0 * (g.percent[3] / 10.0)) / 10.0);
            if (g.isMyst) b.myst |= MYST_RIBBON;
            break;
        case GEAR_HUNT:
            b.sRateB += int(g.lvl * 0.4 * (g.percent[0] / 10.0)) / 10.0;
            hpAdd += tStr * (int(int(g.lvl * 0.08) * (g.percent[1] / 10.0)) / 10.0);
            hpAdd += tAgi * (int(int(g.lvl * 0.08) * (g.percent[2] / 10.0)) / 10.0);
            hpPlus += round(b.hpM * (int(int(g.lvl * 0.06) * (g.percent[3] / 10.0)) / 1000.0) * 100.0) /100.0;
            if (g.isMyst) b.myst |= MYST_HUNT;
            break;
        }
    }
    b.hpM += hpPlus + hpAdd;
    if (pc.role == ROLE_XI)
    {
        b.hpM += pc.growth > 100000 ? 100000 : pc.growth;
    }
    b.pAtkB += pAtkPlus;
    b.mAtkB += mAtkPlus;
    b.spdB += spdPlus;
    b.sRateP = b.sRateB * 100.0 / (b.sRateB + 99.0);
    b.cRateP = b.cRateB * 100.0 / (b.cRateB + 99.0);
    b.sldM += sldPlus + sldAdd;
    if (pc.role == ROLE_XIA)
    {
        b.sldM += pc.growth > 100000 ? 100000 : pc.growth;
    }
    b.hp = b.hpM;
    b.spdRR = 0.0;
    b.spdC = b.spdB + b.spdA;
    b.sld = b.sldM;

    b.alias = pc.alias;
}

inline int calcDefRate(int def, int defP, int brc, int cBrc, int brcA, int defMax, bool isDunh, bool isZhi, int hongBrcA)
{
    if (hongBrcA != -1)
    {
        if (brc < 40)
        {
            brc = 40;
        }
        else
        {
            brcA += hongBrcA;
        }
    }
    int brcP = (int)(brc * (isDunh ? 0.65 : 1.0)) + (int)(cBrc * (isDunh ? 0.65 : 1.0));
    int r = def * (100 + defP - brcP);
    r = (r >= 0 ? r : r - 99) / 100 - brcA;
    r = (r >= 0 ? r / 10 : isZhi && isDunh ? 5 : isZhi ? 10 : -30);
    if (r > defMax) r = defMax;
    if (debug)
    {
        printf("DefRate: def=%d(+%d%%) brc=%d%%+%d dr=%d dunh=%s zhi=%s hongA=%d\n",
            def, defP, brcP, brcA, r,
            isDunh ? "true" : "false", isZhi ? "true" : "false", hongBrcA);
    }
    return r;
}

void showRole(const BStat& b)
{
    if (b.role >= ROLE_PC)
    {
        printf("%s", pcName[b.role - ROLE_PC]);
        if (b.alias.size())
        {
            printf("_%s", b.alias.c_str());
        }
        for (int i = 0; i < AURA_COUNT; ++i)
        {
            if (b.psvSkl & (1 << i))
            {
                printf("_%s", auraName[i]);
            }
        }
    }
    else
    {
        printf("%s", npcName[b.role - ROLE_NPC]);
        if (b.role < ROLE_NPC + NPC_COUNT_OLD)
        {
            for (int i = 0; i < PREF_COUNT; ++i)
            {
                if (b.psvSkl & prefAura[i])
                {
                    printf("_%s", prefName[i]);
                }
            }
        }
    }
    if (b.lvl == -1)
    {
        printf(" Lv.?");
    }
    else
    {
        printf(" Lv.%d", b.lvl);
    }
}

void showRound(bool isC, bool isS, int pa, int ma, int aa, int hd, int sd, int hr, int sr)
{
    bool first = true;
    if (isC) { printf("%sCRT", first ? "" : " "); first = false; }
    if (isS) { printf("%sSKL", first ? "" : " "); first = false; }
    if (pa > 0) { printf("%sP:%d", first ? "" : " ", pa); first = false; }
    if (ma > 0) { printf("%sM:%d", first ? "" : " ", ma); first = false; }
    if (aa > 0) { printf("%sA:%d", first ? "" : " ", aa); first = false; }
    if (hd > 0) { printf("%sH-%d", first ? "" : " ", hd); first = false; }
    if (hr > 0) { printf("%sH+%d", first ? "" : " ", hr); first = false; }
    if (sd > 0) { printf("%sS-%d", first ? "" : " ", sd); first = false; }
    if (sr > 0) { printf("%sS+%d", first ? "" : " ", sr); first = false; }
}

BResult calcBattle(const BStat& attacker, const BStat& defender, bool showDetail, int counter, int* rseed = NULL, bool interact = false)
{
    BStat b[2];
    b[0] = attacker;
    b[1] = defender;
    if (rseed == NULL) rseed = &rseedGlobal;

    for (int i = 0; i < 2; ++i)
    {
        if (b[i].role < ROLE_NPC + NPC_COUNT_OLD)
        {
            int prefixCount = b[i].psvSkl % 5;
            int prefix = b[i].psvSkl / 5;
            int index = counter % prefCount[prefix][prefixCount];
            counter /= prefCount[prefix][prefixCount];
            b[i].psvSkl = prefTable[prefix][prefixCount][index];
        }
        else if (b[i].role == ROLE_LIU)
        {
            prepareLiuStat(b[i], rseed);
        }
    }
    int sRateRdc = ((b[0].sRateB + b[1].sRateB) * reduceRateA + reduceRateB / 2) / reduceRateB;
    int cRateRdc = ((b[0].cRateB + b[1].cRateB) * reduceRateA + reduceRateB / 2) / reduceRateB;
    int mystBladeDmg[2] = { 0, 0 };
    for (int i = 0; i < 2; ++i)
    {
        int hpMAdd = 0;
        int sldMAdd = 0;
        b[i].sRateB = (b[i].sRateB > sRateRdc ? b[i].sRateB - sRateRdc : 0);
        b[i].cRateB = (b[i].cRateB > cRateRdc ? b[i].cRateB - cRateRdc : 0);
        b[i].sRateP = b[i].sRateB * 100 / (b[i].sRateB + 99);
        b[i].cRateP = b[i].cRateB * 100 / (b[i].cRateB + 99);
        b[i].pAtkR = b[i].amul[AMUL_PATK];
        b[i].mAtkR = b[i].amul[AMUL_MATK];
        if (b[i].myst & MYST_BLADE)
        {
            mystBladeDmg[i] = (b[i].pAtkB + b[i].pAtkA) / 2;
        }
        if (b[i].myst & MYST_SHIELD)
        {
            b[1 - i].hpRecRR += 40;
            b[1 - i].sldRecRR += 40;
        }
        if (b[i].myst & MYST_CLAYMORE)
        {
            b[i].cRateP = 100;
        }
        if (b[i].psvSkl & AURA_TIAO && b[i].lvl < b[1 - i].lvl)
        {
            int lvlDiff = b[1 - i].lvl - b[i].lvl;
            if (b[1 - i].role < ROLE_PC && lvlDiff > 100) lvlDiff = 100;
            b[i].pAtkA += lvlDiff * 20;
            b[i].mAtkA += lvlDiff * 20;
            if (b[i].psvSkl & FLAG_STAT && b[i].psvSkl & AURA_BI)
            {
                b[i].pBrcA = (revMul(b[i].pBrcA, 1.15) + lvlDiff * 2) * 1.15;
            }
            else
            {
                b[i].pBrcA += lvlDiff * 2;
            }
            if (b[i].psvSkl & FLAG_STAT && b[i].psvSkl & AURA_MO)
            {
                b[i].mBrcA = (revMul(b[i].mBrcA, 1.15) + lvlDiff * 2) * 1.15;
            }
            else
            {
                b[i].mBrcA += lvlDiff * 2;
            }
        }
        if (b[i].psvSkl & AURA_YA && b[i].lvl > b[1 - i].lvl)
        {
            int lvlDiff = b[i].lvl - b[1 - i].lvl;
            if (b[1 - i].role < ROLE_PC && lvlDiff > 100) lvlDiff = 100;
            if (b[i].psvSkl & FLAG_STAT)
            {
                if (b[i].psvSkl & AURA_JU)
                {
                    b[i].spdA = revMul(b[i].spdA, 1.3);
                    b[i].spdA += lvlDiff * 3;
                    b[i].spdA *= 1.3;
                }
                else
                {
                    b[i].spdA += lvlDiff * 3;
                }
                if (b[i].psvSkl & AURA_DIAN)
                {
                    b[i].pDefA = revMul(b[i].pDefA, 1.3);
                    b[i].mDefA = revMul(b[i].mDefA, 1.3);
                }
                if (b[i].role == ROLE_MING)
                {
                    b[i].pDefA = revMul(b[i].pDefA, 0.5);
                    b[i].mDefA = revMul(b[i].mDefA, 0.5);
                }
                b[i].pDefA += lvlDiff * 3;
                b[i].mDefA += lvlDiff * 3;
                if (b[i].role == ROLE_MING)
                {
                    b[i].pDefA *= 0.5;
                    b[i].mDefA *= 0.5;
                }
                if (b[i].psvSkl & AURA_DIAN)
                {
                    b[i].pDefA *= 1.3;
                    b[i].mDefA *= 1.3;
                }
            }
            else
            {
                b[i].spdA += lvlDiff * 3;
                b[i].pDefA += lvlDiff * 3;
                b[i].mDefA += lvlDiff * 3;
            }
        }
        if (b[i].psvSkl & AURA_XUE)
        {
            b[i].hpRecRR -= 10;
        }
        if (b[i].psvSkl & AURA_SHANG)
        {
            b[1 - i].hpRecRR += 70;
        }
        if (b[i].psvSkl & AURA_SHEN)
        {
            b[1 - i].sldRecRR += 70;
        }
        if (b[i].role == ROLE_WEI)
        {
            b[i].sRateP += 10;
        }
        if (b[i].role == ROLE_WU)
        {
            b[i].pAtkR += 30;
            b[i].mAtkR += 30;
            b[i].spdRR -= 30;
        }
        if (b[i].role == ROLE_XIA)
        {
            b[i].mBrcA += int((b[1 - i].pDefB + b[1 - i].pDefA) * 0.35);
            if (b[i].myst & MYST_LIMPIDWAND)
            {
                b[i].mBrcA += int((b[1 - i].mDefB + b[1 - i].mDefA) * 0.15);
            }
        }
        if (b[i].role == ROLE_MO)
        {
            b[i].mBrcA += int((b[i].tSpr + b[i].tInt) * 0.2);
        }
        b[i].hpRecRR -= b[i].amul[AMUL_REC];
        b[i].sldRecRR -= b[i].amul[AMUL_REC];
        b[i].spdRR -= b[i].amul[AMUL_SPD];
        b[i].cRateP += b[i].amul[AMUL_CRT];
        b[i].sRateP += b[i].amul[AMUL_SKL];
        b[i].cDef += b[i].amul[AMUL_CRTR];
        b[i].sDef += b[i].amul[AMUL_SKLR];
        if (b[i].cRateP > 100) b[i].cRateP = 100;
        if (b[i].sRateP > 100) b[i].sRateP = 100;
        if (!(b[i].psvSkl & FLAG_STAT))
        {
            if (b[i].myst & MYST_CLOAK)
            {
                sldMAdd += 50;
            }
            if (b[i].myst & MYST_THORN)
            {
                b[i].rflP += 25;
            }
            if (b[i].psvSkl & AURA_SHI)
            {
                b[i].pRdc += int(b[i].lvl * 2 * (1 + b[i].wish[WISH_SHI_BUF] * 0.05));
                b[i].mRdc += int(b[i].lvl * 2 * (1 + b[i].wish[WISH_SHI_BUF] * 0.05));
            }
            if (b[i].psvSkl & AURA_FENG)
            {
                b[i].pAtkA += int(b[i].lvl * 5 * (1 + b[i].wish[WISH_FENG_BUF] * 0.05));
                b[i].mAtkA += int(b[i].lvl * 5 * (1 + b[i].wish[WISH_FENG_BUF] * 0.05));
            }
            if (b[i].psvSkl & AURA_XIN)
            {
                b[i].hpM += int(b[i].lvl * 10 * (1 + b[i].wish[WISH_XIN_BUF] * 0.05));
                b[i].sldM += int(b[i].lvl * 10 * (1 + b[i].wish[WISH_XIN_BUF] * 0.05));
            }
            if (b[i].psvSkl & AURA_BI)
            {
                b[i].pBrcP *= 1.15;
                b[i].pBrcA *= 1.15;
            }
            if (b[i].psvSkl & AURA_MO)
            {
                b[i].mBrcP *= 1.15;
                b[i].mBrcA *= 1.15;
            }
            if (b[i].psvSkl & AURA_XUE)
            {
                b[i].lchP += 10;
            }
            if (b[i].psvSkl & AURA_CI)
            {
                b[i].pDefB += b[i].pDefB / 10;
                b[i].mDefB += b[i].mDefB / 10;
                b[i].rflP += 10;
            }
            if (b[i].psvSkl & AURA_JU)
            {
                b[i].spdB = b[i].spdB * 1.3;
                b[i].spdA = b[i].spdA * 1.3;
            }
            if (b[i].role == ROLE_MO)
            {
                sldMAdd += 40;
            }
            if (b[i].role == ROLE_LIN)
            {
                hpMAdd += 30;
            }
            if (b[i].role == ROLE_MENG)
            {
                sldMAdd += (b[i].myst & MYST_TIARA ? 45 : 30);
            }
            if (b[i].role == ROLE_AI)
            {
                b[i].lchP += 15;
            }
            if (b[i].role == ROLE_YI)
            {
                hpMAdd += 20;
            }
            if (b[i].role == ROLE_MING)
            {
                hpMAdd += 90;
                b[i].pDefB *= 0.5;
                b[i].pDefA *= 0.5;
                b[i].mDefB *= 0.5;
                b[i].mDefA *= 0.5;
            }
            if (b[i].role == ROLE_WU)
            {
                hpMAdd += 30;
                sldMAdd += 30;
                b[i].pDefB *= 1.15;
                b[i].mDefB *= 1.15;
            }
            if (b[i].role == ROLE_XI)
            {
                hpMAdd += 10;
            }
            if (b[i].psvSkl & AURA_DIAN)
            {
                b[i].pDefB *= 1.3;
                b[i].pDefA *= 1.3;
                b[i].mDefB *= 1.3;
                b[i].mDefA *= 1.3;
            }
            hpMAdd += b[i].amul[AMUL_HP];
            sldMAdd += b[i].amul[AMUL_SLD];
            b[i].lchP += b[i].amul[AMUL_LCH];
            b[i].rflP += b[i].amul[AMUL_RFL];
            b[i].rflP = b[i].rflP > 150.0 ? 150.0 : b[i].rflP;
        }
        if (b[i].role == ROLE_XIA)
        {
            // Process mAtk growth after AURA_FENG
            if (b[i].mAtkB + b[i].mAtkA > b[1 - i].mAtkB + b[1 - i].mAtkA)
            {
                b[i].mAtkB *= 1.3;
                b[i].mAtkA *= 1.3;
            }
            else
            {
                b[i].spdB *= 1.3;
                b[i].spdA *= 1.3;
            }
        }
        if (b[i].role == ROLE_YA)
        {
            if (b[i].mode == 0)
            {
                b[i].pDefB *= 1.2;
                b[i].pDefA *= 1.2;
                b[i].mDefB *= 1.2;
                b[i].mDefA *= 1.2;
            }
            if (b[i].mode == 1)
            {
                b[1 - i].mAtkB *= 0.7;
                b[1 - i].mAtkA *= 0.7;
                b[1 - i].pAtkB *= 0.7;
                b[1 - i].pAtkA *= 0.7;
                b[1 - i].spdB *= 0.7;
                b[1 - i].spdA *= 0.7;
            }
        }
        b[i].hpM *= 1 + hpMAdd / 100.0;
        b[i].sldM *= 1 + sldMAdd / 100.0;
        b[i].hp = b[i].hpM;
        b[i].sld = b[i].sldM;
        b[i].spdC = b[i].psvSkl & AURA_SHAN ? 1 : (b[i].spdB + b[i].spdA) * (1 - b[i].spdRR / 100.0);
        b[i].hpPot = false;
        b[i].sldPot = false;
        b[i].ziFlag = false;
    }
    //if (b[0].hpRecRR > 100) b[0].hpRecRR = 100;
    //if (b[0].sldRecRR > 100) b[0].sldRecRR = 100;
    if (b[0].role == ROLE_YI && b[0].hpRecRR > 0) b[0].hpRecRR = 0;
    //if (b[1].hpRecRR > 100) b[1].hpRecRR = 100;
    //if (b[1].sldRecRR > 100) b[1].sldRecRR = 100;
    if (b[1].role == ROLE_YI && b[1].hpRecRR > 0) b[1].hpRecRR = 0;

    if (showDetail)
    {
        showRole(b[0]);
        printf("  VS  ");
        showRole(b[1]);
        printf("\n");
        printf("HP:%d SLD:%d  --  HP:%d SLD:%d\n", int(b[0].hp), int(b[0].sld), int(b[1].hp), int(b[1].sld));
    }
    //int roundFlag = 0;
    int roundCounter = 0;
    int lastSide = 0;
    int roundN[2] = { 0, 0 };
    int renCounter = 3;
    if (b[0].tAgi > b[1].tAgi && b[0].tAgi > b[1].tAgi * 6)
    {
        renCounter = 4;
    }
    if (b[1].tAgi > b[0].tAgi && b[1].tAgi > b[0].tAgi * 6)
    {
        renCounter = 4;
    }
    for (int round = 1;; ++round)
    {
        int s = b[0].spdC >= b[1].spdC ? 0 : 1;
        b[s].spdC -= b[1 - s].spdC;
        b[1 - s].spdC = 0;
        if (roundCounter == renCounter && b[1 - lastSide].psvSkl & AURA_REN)
        {
            //b[lastSide].spdC = 0;
            s = 1 - lastSide;
            b[s].spdC = 1;
        }
        BStat& b0 = b[s];
        BStat& b1 = b[1 - s];
        if (s != lastSide)
        {
            lastSide = s;
            roundCounter = 0;
        }
        ++roundCounter;
        ++roundN[s];
        //roundFlag |= (1 << s);
        if (debug)
        {
            printf("Timing: %d(%d*%d%%=%d) %d(%d*%d%%=%d)\n",
                b[0].spdC, b[0].spdA + b[0].spdB, 100 - b[0].spdRR,
                int((b[0].spdA + b[0].spdB) * (1 - b[0].spdRR / 100.0)),
                b[1].spdC, b[1].spdA + b[1].spdB, 100 - b[1].spdRR,
                int((b[1].spdA + b[1].spdB) * (1 - b[1].spdRR / 100.0)));
        }

        int pa[2] = { 0, 0 };
        int ma[2] = { 0, 0 };
        int aa[2] = { 0, 0 };
        int hd[2] = { 0, 0 };
        int hr[2] = { 0, 0 };
        int sd[2] = { 0, 0 };
        int sr[2] = { 0, 0 };

        bool isS, isC, isMC, isE;
        int sklType = 0;
        if (interact)
        {
            for (;;)
            {
                int x;
                printf("%s SKL:1 CRT:2 MCRT:4 E:8 quit:q\n", s == 0 ? "->" : "<-");
                scanf("%s", buf);
                if (strcmp(buf, "q") == 0)
                {
                    BResult br;
                    br.winner = 1;
                    br.rate = 1.0;
                    return br;
                }
                int len = strlen(buf);
                switch (buf[len - 1])
                {
                case 'p':
                    sklType = 1;
                    buf[len - 1] = 0;
                    break;
                case 'm':
                    sklType = 2;
                    buf[len - 1] = 0;
                    break;
                case 'a':
                    sklType = 3;
                    buf[len - 1] = 0;
                    break;
                default:
                    sklType = 0;
                    break;
                }
                if (isNumber(buf) && sscanf(buf, "%d", &x) == 1 && x >= 0 && x <= 15)
                {
                    isS = (x & 1);
                    isC = (x & 2);
                    isMC = (x & 4);
                    isE = (x & 8);
                    if (b0.role == ROLE_MIN && isS && sklType == 0)
                    {
                        printf("Should specify skill type for MIN\n");
                        continue;
                    }
                    break;
                }
                printf("Invalid input\n");
            }
        }
        else
        {
            isS = (rand100(rseed) < b0.sRateP);
            isC = (rand100(rseed) < b0.cRateP);
            isMC = (b0.myst & MYST_BRACELET && rand100(rseed) < 20);
            isE = (b0.psvSkl & AURA_E && rand100(rseed) < 1);
            if (b0.role == ROLE_MO && b0.myst & MYST_WAND && b0.sklC == 0)
            {
                isS = true;
                b0.sklC = 1;
            }
            if (b0.role == ROLE_MIN && isS)
            {
                sklType = myrand(rseed, 3) + 1;
            }
            if (b0.role == ROLE_XI && b1.hp + b1.sld < (b1.hpM + b1.sldM) / 2)
            {
                isC = true;
            }
        }
        pa[s] = b0.pAtkB + b0.pAtkA;
        ma[s] = b0.mAtkB + b0.mAtkA;
        aa[s] = b0.aAtk;
        if (b1.spdRR > speedReduceMax) b1.spdRR = speedReduceMax;
        if (b1.role == ROLE_YI && b1.spdRR > 0) b1.spdRR = 0;
        if (b0.role == ROLE_AI)
        {
            b0.sklC += (b0.myst & MYST_DAGGER ? 2 : 1);
            aa[s] += (b0.pAtkB + b0.pAtkA + b0.mAtkB + b0.mAtkA) * 9 * (b0.myst & MYST_DAGGER ? 20 + b0.sklC * 3 : 20) / 400;
        }
        if (b0.role == ROLE_MENG)
        {
            b0.sklC += 2;
            ma[s] += int(b0.sldM * 0.03 * b0.sklC + (b0.mAtkA + b0.mAtkB) * 0.03 * b0.sklC);
            ++b1.spdRR;
        }
        if (b0.role == ROLE_YI)
        {
            int atkPlus = (int)((b0.pAtkB + b0.pAtkA + b0.mAtkB + b0.mAtkA) * 1.4);
            if (b0.myst & MYST_COLORFUL)
            {
                ma[s] += atkPlus;
                pa[s] += atkPlus;
            }
            else
            {
                if (b1.pDefB + b1.pDefA > b1.mDefB + b1.mDefA)
                {
                    ma[s] += atkPlus;
                }
                else
                {
                    pa[s] += atkPlus;
                }
            }
        }
        if (b0.role == ROLE_WU && b0.myst & MYST_RING)
        {
            pa[s] += (b0.sklC + 100) * 0.2;
            ma[s] += (b0.sklC + 100) * 0.2;
        }
        if (b0.role == ROLE_XI && b0.hp < b0.hpM / 2)
        {
            pa[s] += b0.hpM - b0.hp;
        }
        if (b0.role == ROLE_MIN && b0.sklC > 0) b0.sklC = 0;
        if (b0.psvSkl & AURA_XIAO)
        {
            aa[s] += int(b1.hpM * 0.015) + int(b1.sldM * 0.015);
        }
        if (b0.psvSkl & AURA_WU && round > 15)
        {
            aa[s] += int((b0.pAtkB + b0.pAtkA + b0.mAtkB + b0.mAtkA) * 0.25);
        }
        if (b0.psvSkl & AURA_FEI)
        {
            pa[s] += int(b0.hpM * 0.18);
        }
        if (b0.myst & MYST_ASSBOW)
        {
            pa[s] += b1.sld * 3 / 10;
        }
        if (b0.myst & MYST_SPEAR)
        {
            ma[s] += b1.hp * 3 / 10;
        }
        if (isE)
        {
            pa[s] += (b0.pAtkB + b0.pAtkA) * 30;
            ma[s] += (b0.mAtkB + b0.mAtkA) * 30;
        }
        if (b0.role == ROLE_YA)
        {
            pa[s] += (int)((b0.mAtkB + b0.mAtkA) * 0.2 * round);
            pa[s] += (int)((b0.pAtkB + b0.pAtkA) * 0.2 * round);
        }
        if (isC)
        {
            pa[s] *= 2;
            ma[s] += ma[s] / 2;
            aa[s] *= 2;
            if (b0.role == ROLE_MIN)
            {
                pa[s] += pa[s] * 0.65;
                ma[s] += ma[s] * 0.65;
                aa[s] += aa[s] * 0.65;
            }
            if (b0.role == ROLE_LIN && b0.sklC == 0)
            {
                pa[s] += b0.hpM * 0.5;
                b0.sklC = 1;
            }
            if (b0.psvSkl & AURA_JU)
            {
                int spd = int((b0.spdB + b0.spdA) * (1 - b0.spdRR / 100.0));
                if (spd <= 0) spd = 1;
                int spd2 = int((b1.spdB + b1.spdA) * (1 - b1.spdRR / 100.0));
                if (spd2 <= 0) spd2 = 1;
                aa[s] += (spd > spd2 * 3 ? spd * 12 : spd * 9) / 5;
            }
            if (b0.myst & MYST_BLADE)
            {
                aa[s] += mystBladeDmg[s];
            }
        }
        if (isS)
        {
            switch (b0.role)
            {
            case ROLE_MU:
                pa[s] += b0.pAtkB * 3;
                hr[s] += b0.hpM / 10;
                break;
            case ROLE_ZHU:
                ma[s] += b0.mAtkB;
                b1.spdRR += 20;
                break;
            case ROLE_DENG:
                ma[s] += b0.sld * 3 / 10;
                sr[s] += b0.sldM / 10;
                break;
            case ROLE_SHOU:
                pa[s] += b0.hpM / 5;
                hr[s] += b0.hpM * 3 / 10;
                break;
            case ROLE_MU2:
            case ROLE_YU2:
                pa[s] += b0.pAtkB * 5;
                break;
            case ROLE_ZHU2:
                ma[s] += b0.mAtkB * 5;
                break;
            case ROLE_DENG2:
                ma[s] += b0.sldM * 2 / 5;
                break;
            case ROLE_SHOU2:
            case ROLE_HAO2:
            case ROLE_LIU:
                pa[s] += b0.hpM * 2 / 5;
                break;
            case ROLE_SHI:
                pa[s] += b0.pAtkB * 3;
                ma[s] += b0.mAtkB * 3;
                aa[s] += pa[s] + ma[s];
                break;
            case ROLE_MO:
            {
                int maDif = 0;
                if (b0.tSpr > b0.tInt)
                {
                    maDif = int(int((b0.tSpr / b0.tInt - 1) * 100) / 2);
                }
                else
                {
                    maDif = int(int((b0.tInt / b0.tSpr - 1) * 100) / 2);
                }
                maDif = maDif > 1000 ? 1000 : maDif;
                double atk = ((b0.mAtkB + b0.mAtkA) * 0.35 + b0.sldM * 0.05) * (1 + maDif / 100.0);
                ma[s] += int(atk);
                if (b0.myst & MYST_WAND) ma[s] += int(atk * 0.4);
                break;
            }
            case ROLE_LIN:
            {
                int dmg = (b0.pAtkB + b0.pAtkA) * 3;
                pa[s] += dmg;
                ma[s] += dmg;
                break;
            }
            case ROLE_AI:
                aa[s] += int((b1.hp + b1.sld) * 0.13 * b0.sklC);
                b0.sklC = 0;
                break;
            case ROLE_MENG:
                b0.sklC += 7;
                ma[s] += (b0.mAtkB + b0.mAtkA) * b0.sklC / 4;
                b1.spdRR += b0.sklC / 2;
                if (b1.spdRR > 100) b1.spdRR = 100;
                break;
            case ROLE_WEI:
                b0.sklC = 1;
                break;
            case ROLE_YI:
            {
                int dmg = (int)(((b1.sld > b1.hp) ? b1.sld : b1.hp) * 0.15);
                aa[s] += dmg;
                hr[s] += dmg;
                break;
            }
            case ROLE_MING:
            {
                int dmg = b0.hpM - b0.hp;
                ma[s] += dmg;
                hr[s] += dmg / 2;
                break;
            }
            case ROLE_MIN:
                b0.sklC = -sklType;
                break;
            case ROLE_WU:
                pa[s] += b0.sklC + 100;
                ma[s] += b0.sklC + 100;
                break;
            case ROLE_XI:
            {
                int hpRate = (b0.hpM - b0.hp) * 100 / b0.hpM;
                int dmg = (b0.pAtkB + b0.pAtkA) * 3 * (1 + hpRate / 100.0);
                if (b0.hp + b0.sld < (b0.hpM + b0.sldM) / 10 ||
                    b1.hp + b1.sld < (b1.hpM + b1.sldM) / 10)
                {
                    aa[s] += dmg;
                }
                else
                {
                    pa[s] += dmg;
                }
                break;
            }
            case ROLE_XIA:
            {
                int dmgAdd = (b1.mDefB + b1.mDefA) / 10;
                if (dmgAdd > 200) dmgAdd = 200;
                ma[s] += (b0.mAtkB + b0.mAtkA) * 2 * (1 + dmgAdd / 100.0);
                break;
            }
            case ROLE_YA:
            {
                b0.pAtkB += (b1.hpM + b1.sldM) * 0.05;
                pa[s] += (b0.pAtkB + b0.pAtkA) * 3;
                b1.hpM *= 0.95;
                b1.sldM *= 0.95;
                break;
            }
            }
        }
        if (b0.role == ROLE_WEI)
        {
            int pAdd = int((b1.hpM + b1.sldM) * 0.21);
            if (b0.myst & MYST_HUNT)
            {
                pa[s] += pAdd * 0.7;
                aa[s] += pAdd * 0.3;
            }
            else
            {
                pa[s] += pAdd;
            }
            if (b0.sklC) pa[s] = int(pa[s] * 1.4);
        }
        if (isMC)
        {
            ma[s] *= 2;
        }
        if (b0.psvSkl & AURA_HOU)
        {
            pa[s] = int(pa[s] * (1 + b0.houC * 0.24));
            ma[s] = int(ma[s] * (1 + b0.houC * 0.24));
            aa[s] = int(aa[s] * (1 + b0.houC * 0.24));
            b0.houC = 0;
        }
        if (b1.psvSkl & AURA_HOU) ++b1.houC;
        pa[s] = int(pa[s] * (1 + b0.pAtkR * 0.01));
        ma[s] = int(ma[s] * (1 + b0.mAtkR * 0.01));

        int rflPFixed = (b0.psvSkl & AURA_DI ? b1.rflP / 2 : b1.rflP);
        int pRfl = 0;
        int mRfl = (pa[s] * 0.7 + ma[s] * 0.7 + aa[s] * 0.5) * (rflPFixed / 100.0);
        if (b1.role == ROLE_MO) mRfl += int((((b1.mAtkB + b1.mAtkA) * 0.55) + b1.sldM * 0.07) * (1 + b1.mAtkR * 0.01));

        if (b0.role == ROLE_MING)
        {
            pa[s] += pRfl * 2 / 5;
            ma[s] += mRfl * 2 / 5;
        }
        if (b1.role == ROLE_MING)
        {
            pRfl += pa[s] * 2 / 5;
            mRfl += ma[s] * 2 / 5;
        }

        if (b1.myst & MYST_CAPE)
        {
            int convert = pa[s] / 2;
            pa[s] -= convert;
            ma[s] += convert;
        }
        if (b0.psvSkl & AURA_DIAN)
        {
            pa[s] *= 0.7;
            ma[s] *= 0.7;
        }
        if (b1.psvSkl & AURA_DIAN)
        {
            pRfl *= 0.7;
            mRfl *= 0.7;
        }
        if (b0.psvSkl & AURA_ZI)
        {
            if (!b0.ziFlag)
            {
                b0.ziFlag = true;
                pa[s] *= 1.5;
                ma[s] *= 1.5;
                aa[s] *= 1.5;
            }
            else
            {
                pa[s] *= 0.9;
                ma[s] *= 0.9;
                aa[s] *= 0.9;
            }
        }
        if (b0.atkLvl > b1.atkLvl && b1.atkLvl > 0 && b0.atkLvl > 0)
        {
            int lvlDiff = b0.atkLvl - b1.atkLvl > 20 ? 20 : b0.atkLvl - b1.atkLvl;
            pa[s] *= 1 + 0.03 * lvlDiff;
            ma[s] *= 1 + 0.03 * lvlDiff;
            aa[s] *= 1 + 0.03 * lvlDiff;
        }
        if (isC)
        {
            pa[s] *= (1 - b1.cDef / 100.0);
            ma[s] *= (1 - b1.cDef / 100.0);
            aa[s] *= (1 - b1.cDef / 100.0);
        }
        if (isS)
        {
            pa[s] *= (1 - b1.sDef / 100.0);
            ma[s] *= (1 - b1.sDef / 100.0);
            aa[s] *= (1 - b1.sDef / 100.0);
        }

        int sldRemain = b1.sld;
        bool sldActive = (sldRemain > 0);
        if (ma[s] > 0)
        {

            int dr = calcDefRate(b1.mDefB + b1.mDefA, b1.amul[AMUL_MDEF],
                b0.mBrcP + (b0.psvSkl & AURA_BO && (b0.hp > b0.hpM * 0.7 && b0.sld > b0.sldM * 0.7) ? 30 : 0),
                isC ? b0.cBrcP : 0, b0.mBrcA,
                (b1.psvSkl & AURA_SHENG) ? 80 : 75,
                b1.psvSkl & AURA_DUNH, b1.psvSkl & AURA_ZHI,
                (b0.psvSkl & AURA_HONG) ? b0.lvl / 2 : -1);
            int ma2 = ma[s];
            if (b1.defLvl > b0.defLvl && b1.defLvl > 0 && b0.defLvl > 0)
            {
                int lvlDiff = b1.defLvl - b0.defLvl > 20 ? 20 : b1.defLvl - b0.defLvl;
                ma2 *= 1 - 0.03 * lvlDiff;
            }
            ma[s] = ma2;
            if (b1.role == ROLE_MIN && (b1.sklC > 0 || b1.sklC == -2)) ma2 = 0;
            if (b1.role == ROLE_WEI && b1.sklC) ma2 /= 10;
            if (b1.psvSkl & AURA_JUE) ma2 *= 0.8;
            if (b1.psvSkl & AURA_DI) ma2 *= 0.1;
            if (sldActive)
            {
                int sdMax = int(ma2 * (dr >= 0 ? 1 - dr / 200.0 : 1 - dr / 100.0)) - b1.mRdc;
                if (sdMax < 0) sdMax = 0;
                if (debug && sdMax > 0)
                {
                    printf("MA-SLD: ma=%d sld=%d\n", ma2, sdMax);
                }
                if (sdMax <= sldRemain)
                {
                    sldRemain -= sdMax;
                    sd[1 - s] += sdMax;
                    ma2 = 0;
                }
                else
                {
                    ma2 = (sdMax - sldRemain) / (dr >= 0 ? 1 - dr / 200.0 : 1 - dr / 100.0);
                    sd[1 - s] += sldRemain;
                    sldRemain = 0;
                    sldActive = false;
                }
            }
            int hd2 = int(ma2 * (1 - dr / 100.0)) - b1.mRdc;
            if (debug && ma2 > 0)
            {
                printf("MA-HP: ma=%d hd=%d\n", ma2, hd2);
            }
            if (hd2 < 0) hd2 = 0;
            hd[1 - s] += hd2;
        }
        if (pa[s] > 0)
        {
            int dr = calcDefRate(b1.pDefB + b1.pDefA, b1.amul[AMUL_PDEF],
                b0.pBrcP, isC ? b0.cBrcP : 0, b0.pBrcA,
                (b1.psvSkl & AURA_SHENG) ? 80 : 75,
                b1.psvSkl & AURA_DUNH, b1.psvSkl & AURA_ZHI,
                (b0.psvSkl & AURA_HONG) ? b0.lvl / 2 : -1);
            int pa2 = pa[s];
            if (b1.defLvl > b0.defLvl && b1.defLvl > 0 && b0.defLvl > 0)
            {
                int lvlDiff = b1.defLvl - b0.defLvl > 20 ? 20 : b1.defLvl - b0.defLvl;
                pa2 *= 1 - 0.03 * lvlDiff;
            }
            pa[s] = pa2;
            if (b1.role == ROLE_MIN && (b1.sklC > 0 || b1.sklC == -1)) pa2 = 0;
            if (b1.role == ROLE_WEI && b1.sklC) pa2 /= 10;
            if (b1.psvSkl & AURA_JUE) pa2 *= 0.8;
            if (b1.psvSkl & AURA_DI) pa2 *= 0.1;
            if (sldActive)
            {
                int sdMax = int(pa2 * (b1.psvSkl & AURA_DUN ? 1.25 : 1.5) * (dr >= 0 ? 1 - dr / 200.0 : 1 - dr / 100.0)) - b1.pRdc;
                if (sdMax < 0) sdMax = 0;
                if (debug && sdMax > 0)
                {
                    printf("PA-SLD: pa=%d sld=%d\n", pa2, sdMax);
                }
                if (sdMax <= sldRemain)
                {
                    sldRemain -= sdMax;
                    sd[1 - s] += sdMax;
                    pa2 = 0;
                }
                else
                {
                    pa2 = (sdMax - sldRemain) / (dr >= 0 ? 1 - dr / 200.0 : 1 - dr / 100.0) / (b1.psvSkl & AURA_DUN ? 1.25 : 1.5);
                    sd[1 - s] += sldRemain;
                    sldRemain = 0;
                    sldActive = false;
                }
            }
            int hd2 = int(pa2 * (1 - dr / 100.0)) - b1.pRdc;
            if (debug && pa2 > 0)
            {
                printf("PA-HP: pa=%d hd=%d\n", pa2, hd2);
            }
            if (hd2 < 0) hd2 = 0;
            hd[1 - s] += hd2;
        }
        if (aa[s] > 0)
        {
            int aa2 = aa[s];
            if (b1.defLvl > b0.defLvl && b1.defLvl > 0 && b0.defLvl > 0)
            {
                int lvlDiff = b1.defLvl - b0.defLvl > 20 ? 20 : b1.defLvl - b0.defLvl;
                aa2 *= 1 - 0.03 * lvlDiff;
            }
            aa[s] = aa2;
            if (b1.role == ROLE_MIN && (b1.sklC > 0 || b1.sklC == -3)) aa2 = 0;
            if (b1.role == ROLE_WEI && b1.sklC) aa2 /= 10;
            // if (b1.psvSkl & AURA_JUE) aa2 *= 1;
            if (b1.psvSkl & AURA_DI) aa2 *= 0.12;
            if (sldActive)
            {
                if (aa2 <= sldRemain)
                {
                    sldRemain -= aa2;
                    sd[1 - s] += aa2;
                    aa2 = 0;
                }
                else
                {
                    aa2 -= sldRemain;
                    sd[1 - s] += sldRemain;
                    sldRemain = 0;
                    sldActive = false;
                }
            }
            hd[1 - s] += aa2;
        }
        if (b1.role == ROLE_WEI && b1.sklC) b1.sklC = 0;

        hr[s] += ((int64_t)hd[1 - s]) * b0.lchP / 100;
        sr[s] += ((int64_t)sd[1 - s]) * b0.lchP / 125;
        if (b0.myst & MYST_VULTURE) hr[s] += ((int64_t)sd[1 - s]) * b0.lchP / 625;

        sldRemain = b0.sld;
        sldActive = (sldRemain > 0);
        if (mRfl > 0)
        {
            int dr = calcDefRate(b0.mDefB + b0.mDefA, b0.amul[AMUL_MDEF],
                b1.mBrcP + (b1.psvSkl & AURA_BO && (b1.hp > b1.hpM * 0.7 && b1.sld > b1.sldM * 0.7) ? 30 : 0),
                0, b1.mBrcA, (b0.psvSkl & AURA_SHENG) ? 80 : 75,
                b0.psvSkl & AURA_DUNH, b0.psvSkl & AURA_ZHI, -1);
            int ma2 = mRfl;
            if (b1.atkLvl > b0.atkLvl && b1.atkLvl > 0 && b0.atkLvl > 0)
            {
                int lvlDiff = b1.atkLvl - b0.atkLvl > 20 ? 20 : b1.atkLvl - b0.atkLvl;
                ma2 *= 1 + 0.03 * lvlDiff;
            }
            if (b1.defLvl < b0.defLvl && b1.defLvl > 0 && b0.defLvl > 0)
            {
                int lvlDiff = b0.defLvl - b1.defLvl > 20 ? 20 : b0.defLvl - b1.defLvl;
                ma2 *= 1 - 0.03 * lvlDiff;
            }
            ma[1 - s] = ma2;
            if (b0.role == ROLE_MIN && b0.sklC == -2) ma2 = 0;
            if (b0.psvSkl & AURA_JUE) ma2 *= 0.8;
            if (b0.psvSkl & AURA_DI) ma2 *= 0.1;
            if (b1.role == ROLE_MIN && b1.sklC > 0) ma2 *= 1;
            if (sldActive)
            {
                int sdMax = int(ma2 * (dr >= 0 ? 1 - dr / 200.0 : 1 - dr / 100.0)) - b0.mRdc;
                if (sdMax < 0) sdMax = 0;
                if (sdMax <= sldRemain)
                {
                    sldRemain -= sdMax;
                    sd[s] += sdMax;
                    ma2 = 0;
                }
                else
                {
                    ma2 = (sdMax - sldRemain) / (dr >= 0 ? 1 - dr / 200.0 : 1 - dr / 100.0);
                    sd[s] += sldRemain;
                    sldRemain = 0;
                    sldActive = false;
                }
            }
            int hd2 = int(ma2 * (1 - dr / 100.0)) - b0.mRdc;
            if (debug && ma2 > 0)
            {
                printf("MR-HP: ma=%d hd=%d\n", ma2, hd2);
            }
            if (hd2 < 0) hd2 = 0;
            hd[s] += hd2;
        }
        if (pRfl > 0)
        {
            int dr = calcDefRate(b0.pDefB + b0.pDefA, b0.amul[AMUL_PDEF],
                b1.pBrcP, 0, b1.pBrcA,
                (b0.psvSkl & AURA_SHENG) ? 80 : 75,
                b0.psvSkl & AURA_DUNH, b0.psvSkl & AURA_ZHI, -1);
            int pa2 = pRfl;
            if (b1.atkLvl > b0.atkLvl && b1.atkLvl > 0 && b0.atkLvl > 0)
            {
                int lvlDiff = b1.atkLvl - b0.atkLvl > 20 ? 20 : b1.atkLvl - b0.atkLvl;
                pa2 *= 1 + 0.03 * lvlDiff;
            }
            if (b1.defLvl < b0.defLvl && b1.defLvl > 0 && b0.defLvl > 0)
            {
                int lvlDiff = b0.defLvl - b1.defLvl > 20 ? 20 : b0.defLvl - b1.defLvl;
                pa2 *= 1 - 0.03 * lvlDiff;
            }
            pa[1 - s] = pa2;
            if (b0.role == ROLE_MIN && b0.sklC == -1) pa2 = 0;
            if (b0.psvSkl & AURA_JUE) pa2 *= 0.8;
            if (b0.psvSkl & AURA_DI) pa2 *= 0.1;
            if (sldActive)
            {
                int sdMax = int(pa2 * (b0.psvSkl & AURA_DUN ? 1.25 : 1.5) * (dr >= 0 ? 1 - dr / 200.0 : 1 - dr / 100.0)) - b0.pRdc;
                if (sdMax < 0) sdMax = 0;
                if (sdMax <= sldRemain)
                {
                    sldRemain -= sdMax;
                    sd[s] += sdMax;
                    pa2 = 0;
                }
                else
                {
                    pa2 = (sdMax - sldRemain) / (dr >= 0 ? 1 - dr / 200.0 : 1 - dr / 100.0) / (b0.psvSkl & AURA_DUN ? 1.25 : 1.5);
                    sd[s] += sldRemain;
                    sldRemain = 0;
                    sldActive = false;
                }
            }
            int hd2 = int(pa2 * (1 - dr / 100.0)) - b0.pRdc;
            if (debug && pa2 > 0)
            {
                printf("PR-HP: pa=%d hd=%d\n", pa2, hd2);
            }
            if (hd2 < 0) hd2 = 0;
            hd[s] += hd2;
        }
        hr[1 - s] += ((int64_t)hd[s]) * b1.lchP / 200;
        sr[1 - s] += ((int64_t)sd[s]) * b1.lchP / 250;
        if (b1.myst & MYST_VULTURE) hr[1 - s] += ((int64_t)sd[s]) * b1.lchP / 1250;
        if (b1.myst & MYST_WOOD)
        {
            hr[1 - s] += b1.hpM / 20;
        }
        if (!b1.hpPot && b1.hp <= b1.hpM * 4 / 5)
        {
            hr[1 - s] += b1.hpM * b1.wish[WISH_HP_POT] / 200;
            b1.hpPot = true;
        }
        if (!b1.sldPot && b1.sld <= b1.sldM * 4 / 5)
        {
            sr[1 - s] += b1.sldM * b1.wish[WISH_SLD_POT] / 200;
            b1.sldPot = true;
        }
        if (b1.role == ROLE_MIN && b1.sklC > 0) --b1.sklC;

        if (b0.spdRR > speedReduceMax) b0.spdRR = speedReduceMax;
        if (b0.role == ROLE_YI && b0.spdRR > 0) b0.spdRR = 0;
        if (b1.role == ROLE_MENG)
        {
            ++b1.sklC;
            b0.spdRR += (b1.myst & MYST_TIARA ? 4 : 2);
        }
        if (b0.psvSkl & AURA_RE)
        {
            b0.spdRR -= 9;
        }

        //if (roundFlag == 3)
        {
            for (int i = 0; i < 2; ++i)
            {
                if (b[i].role == ROLE_LIN)
                {
                    if (b[i].myst & MYST_RIBBON)
                    {
                        hr[i] += b[i].hpM * 3 / 50;
                    }
                    else
                    {
                        if (b[i].hp < b[i].hpM * 3 / 10)
                        {
                            hr[i] += b[i].hpM * 3 / 50;
                        }
                        else
                        {
                            hr[i] += b[i].hpM * 3 / 100;
                        }
                    }
                }
                hr[i] += (b[i].hpM * b[i].hpRecP / 100 + b[i].hpRecA) / 4;
                sr[i] += (b[i].sldM * b[i].sldRecP / 100 + b[i].sldRecA) / 4;
                if (debug)
                {
                    printf("side=%d hp=%d hd=%d hr=%d sld=%d sd=%d sr=%d\n",
                        i, b[i].hp, hd[i], hr[i], b[i].sld, sd[i], sr[i]);
                }
                if (hd[i] >= b[i].hp)
                {
                    hr[i] = 0;
                    sr[i] = 0;
                }
            }
            //roundFlag = 0;
        }

        if (b0.role == ROLE_MING)
        {
            hr[s] += int(hr[1 - s] * 0.6);
            sr[s] += int(sr[1 - s] * 0.6);
            if (b0.myst & MYST_DEVOUR)
            {
                hr[s] += int(sr[1 - s] * 0.3);
            }
        }
        if (b1.role == ROLE_MING)
        {
            hr[1 - s] += int(hr[s] * 0.6);
            sr[1 - s] += int(sr[s] * 0.6);
            if (b1.myst & MYST_DEVOUR)
            {
                hr[1 - s] += int(sr[s] * 0.3);
            }
        }

        for (int i = 0; i < 2; ++i)
        {
            hr[i] = hr[i] * (1 - (b[i].hpRecRR > 100 ? 100 : b[i].hpRecRR) / 100.0);
            sr[i] = sr[i] * (1 - (b[i].sldRecRR > 100 ? 100 : b[i].sldRecRR) / 100.0);
            if (i == 1 - s && b[i].role == ROLE_LIN && b[i].sklC == 0 && hd[i] >= b[i].hp + hr[i])
            {
                hd[i] = 0;
                sd[i] = 0;
                b[i].sklC = 1;
            }
            b[i].hp = b[i].hp - hd[i] + hr[i];
            if (b[i].hp > b[i].hpM) b[i].hp = b[i].hpM;
            if (b[i].hp < 0) b[i].hp = 0;
            b[i].sld = b[i].sld - sd[i] + sr[i];
            if (b[i].sld > b[i].sldM) b[i].sld = b[i].sldM;
        }

        if (showDetail)
        {
            printf("  %d/%d ", roundN[s], roundN[0] + roundN[1]);
            showRound(s == 0 && isC, s == 0 && isS,
                pa[0], ma[0], aa[0], hd[0], sd[0], hr[0], sr[0]);
            printf("  %s  ", s == 0 ? "->" : "<-");
            showRound(s == 1 && isC, s == 1 && isS,
                pa[1], ma[1], aa[1], hd[1], sd[1], hr[1], sr[1]);
            printf("\n");
            printf("HP:%d SLD:%d  --  HP:%d SLD:%d\n", int(b[0].hp), int(b[0].sld), int(b[1].hp), int(b[1].sld));
        }

        int wf = 0;
        for (int i = 0; i < 2; ++i)
        {
            if (b[i].hp == 0)
            {
                wf |= 1 << (1 - i);
            }
        }
        if (wf)
        {
            BResult br;
            br.winner = wf - 1;
            br.rate = (wf == 3 ? 1.0 :
                1.0 * (b[wf - 1].hp + b[wf - 1].sld) / (b[wf - 1].hpM + b[wf - 1].sldM));
            return br;
        }

        b1.spdC = b1.psvSkl & AURA_SHAN ? 1 : (b1.spdB + b1.spdA) * (1 - b1.spdRR / 100.0);
        if (b1.spdC <= 0) b1.spdC = 1;

        if (round == 100) break;
    }

    if (showDetail)
    {
        printf("Over 100 rounds\n");
    }

    BResult br;
    br.winner = 2;
    br.rate = 1;
    return br;
}

void showState(const BStat& b)
{
    printf("Role                   : %s\n",
        b.role >= ROLE_PC ? pcName[b.role - ROLE_PC] : npcName[b.role - ROLE_NPC]);
    printf("Level                  : %d\n", b.lvl);
    printf("Max HP                 : %.2f\n", b.hpM);
    printf("HP Recover             : %.2f%%+%.2f\n", b.hpRecP, b.hpRecA);
    printf("Physical Attack        : %.2f+%.2f\n", b.pAtkB, b.pAtkA);
    printf("Magical Attack         : %.2f+%.2f\n", b.mAtkB, b.mAtkA);
    printf("Absolute Attack        : %.2f\n", b.aAtk);
    printf("Attack Speed           : %.2f+%.2f\n", b.spdB, b.spdA);
    printf("Physical Breach        : %.2f%%+%.2f\n", b.pBrcP, b.pBrcA);
    printf("Magical Breach         : %.2f%%+%.2f\n", b.mBrcP, b.mBrcA);
    printf("Skill Rate             : %.2f(%.2f%%)\n", b.sRateB, b.sRateP);
    printf("Critical Rate          : %.2f(%.2f%%)\n", b.cRateB, b.cRateP);
    printf("Critical Breach        : %.2f%%\n", b.cBrcP);
    printf("Life Steal             : %.2f%%\n", b.lchP);
    printf("Physical Defence       : %.2f+%.2f(%d%%)\n", b.pDefB, b.pDefA, calcDefRate(b.pDefB + b.pDefA, 0, 0, 0, 0, 9999, false, false, -1));
    printf("Magical Defence        : %.2f+%.2f(%d%%)\n", b.mDefB, b.mDefA, calcDefRate(b.mDefB + b.mDefA, 0, 0, 0, 0, 9999, false, false, -1));
    printf("Physical Damage Reduce : %.2f\n", b.pRdc);
    printf("Magical Damage Reduce  : %.2f\n", b.mRdc);
    printf("Max Shield             : %.2f\n", b.sldM);
    printf("Shield Recover         : %.2f%%+%.2f\n", b.sldRecP, b.sldRecA);
    printf("Damage Reflection      : %.2f%%\n", b.rflP);
    printf("Critical Defence       : %.2f%%\n", b.cDef);
    printf("Skill Defence          : %.2f%%\n", b.sDef);
    printf("Attack Level           : %d\n", b.atkLvl);
    printf("Defence Level          : %d\n", b.defLvl);
    printf("Aura Skill Set         :");
    for (int i = 0; i < AURA_COUNT; ++i)
    {
        if (b.psvSkl & 1 << i) printf(" %s", auraName[i]);
    }
    printf("\n");
    printf("Aura Filter            :");
    for (int i = 0; i < AURA_COUNT; ++i)
    {
        if (auraFilter & 1 << i) printf(" %s", auraName[i]);
    }
    printf("\n");
    printf("Wish Points            :");
    for (int i = 0; i < WISH_COUNT; ++i)
    {
        printf(" %d", int(b.wish[i]));
    }
    printf("\n");
    printf("Amulet Points          :");
    for (int i = 0; i < AMUL_COUNT; ++i)
    {
        if (b.amul[i] > 0)
        {
            printf(" %s+%d", amulName[i], b.amul[i]);
            if (i > AMUL_MND) printf("%%");
        }
    }
    printf("\n");
}

AttrScore calcScoreNpc(const BStat& stat, bool showDetail, bool showCI, int* rseed = NULL)
{
    double totalWinRate = 0;
    double totalHpRate = 0;
    double totalWeight = 0;
    for (int i = 0; i < (int)npcEnemy.size(); ++i)
    {
        int win = 0;
        int draw = 0;
        double singleHpRate = 0;
        int numTests2 = numTests;
        int prefixN = 1;
        if (npcEnemyStat[i].role < ROLE_NPC + NPC_COUNT_OLD)
        {
            int prefixCount = npcEnemyStat[i].psvSkl % 5;
            int prefix = npcEnemyStat[i].psvSkl / 5;
            prefixN = prefCount[prefix][prefixCount];
            numTests2 = ((numTests - 1) / prefixN + 1) * prefixN;
        }
        for (int j = 0;; ++j)
        {
            if (ciTest == 0 && j >= numTests2) break;
            BResult br = calcBattle(stat, npcEnemyStat[i], false, j, rseed);
            if (br.winner == 0)
            {
                ++win;
            }
            else if (br.winner == 2)
            {
                ++draw;
            }
            else
            {
                singleHpRate += 1 - br.rate;
            }
            if (ciTest > 0 && j % prefixN == prefixN - 1)
            {
                double low, high;
                ci(win + draw / 2, j + 1, low, high);
                if (high - low < ciTest || j >= 99999999)
                {
                    numTests2 = j + 1;
                    break;
                }
            }
        }
        double winRate = (numTests2 == draw ? 0.5 : 1.0 * win / (numTests2 - draw));
        double weight = 1.0 * (numTests2 - draw) / numTests2;
        if (showDetail)
        {
            printf("%3d: %s", i, npcName[npcEnemy[i].role - ROLE_NPC]);
            if (npcEnemy[i].role < ROLE_NPC + NPC_COUNT_OLD)
            {
                int prefN = 0;
                for (int j = 0; j < PREF_COUNT; ++j)
                {
                    if (npcEnemy[i].prefix & 1 << j)
                    {
                        ++prefN;
                        printf("_%s", prefName[j]);
                    }
                }
                for (int j = 0; j < npcEnemy[i].prefixCount - prefN; ++j)
                {
                    printf("_?");
                }
            }
            else if (npcEnemy[i].role == ROLE_LIU)
            {
                if (npcEnemy[i].prefix != 0x3FFFFFFF)
                {
                    printf("_");
                    for (int j = 0; j < 6; ++j)
                    {
                        int v = (npcEnemy[i].prefix >> (j * 2) & 3);
                        if (v == 3) printf("?");
                        else printf("%d", v);
                    }
                    for (int j = 0; j < 2; ++j)
                    {
                        int v = (npcEnemy[i].prefix >> (j * 6 + 12) & 63);
                        if (v == 63) printf("???");
                        else printf("%d", v + 280);
                    }
                    for (int j = 0; j < 2; ++j)
                    {
                        int v = (npcEnemy[i].prefix >> (j * 3 + 24) & 7);
                        if (v == 7) printf("??");
                        else printf("%d", v + 28);
                    }
                }
            }
            printf(" Lv.%d : Win Rate : %.5lf%% (%d/%d D=%d(%.1lf%%))", npcEnemy[i].lvl,
                winRate * 100, win, numTests2 - draw, draw, 100.0 * draw / numTests2);
            if (showCI)
            {
                double low, high;
                ci(win, numTests2 - draw, low, high);
                printf(" 95%% CI : [%.5lf%%, %.5lf%%]\n", low * 100, high * 100);
            }
            else
            {
                printf("\n");
            }
        }
        totalWinRate += winRate * weight;
        totalHpRate += singleHpRate / numTests2;
        totalWeight += weight;
    }
    if (totalWeight == 0.0)
    {
        totalWinRate = 0.5;
        totalHpRate = 1.0;
    }
    else
    {
        totalWinRate /= totalWeight;
        totalHpRate /= totalWeight;
    }
    if (showDetail)
    {
        printf("Average Win Rate : %.5lf%%\n", 100.0 * totalWinRate);
    }
    return AttrScore(totalWinRate, totalHpRate);
}

AttrScore calcScorePc(const BStat& stat, bool showDetail, bool showCI, int* rseed = NULL)
{
    double totalWinRate = 0;
    double totalHpRate = 0;
    double totalWeight = 0;
    for (int i = 0; i < (int)pcEnemy.size(); ++i)
    {
        if ((defMode == 0 && pcEnemy[i].type == 1) ||
            (defMode == 1 && pcEnemy[i].type == 2)) continue;
        int defMode2, numTests2;
        double weight;
        if (defMode < 2 || pcEnemy[i].type == 3)
        {
            defMode2 = defMode;
            numTests2 = numTests;
            weight = pcEnemy[i].weight;
        }
        else
        {
            defMode2 = 2 - pcEnemy[i].type;
            numTests2 = numTests / 2;
            weight = pcEnemy[i].weight / 2;
        }
        int win = 0;
        int draw = 0;
        double singleHpRate = 0;
        for (int j = 0;; ++j)
        {
            if (ciTest == 0 && j >= numTests2) break;
            bool defTemp = (defMode2 == 1 || (defMode2 == 2 && j & 1));
            BResult br = (defTemp ? calcBattle(pcEnemyStat[i], stat, false, j, rseed)
                : calcBattle(stat, pcEnemyStat[i], false, j, rseed));
            if (br.winner == (defTemp ? 1 : 0))
            {
                ++win;
            }
            else if (br.winner == 2)
            {
                ++draw;
            }
            else
            {
                singleHpRate += 1 - br.rate;
            }
            if (ciTest > 0 && (defMode2 < 2 || j % 2 == 1))
            {
                double low, high;
                ci(win + draw / 2, j + 1, low, high);
                if (high - low < ciTest || j >= 99999999)
                {
                    numTests2 = j + 1;
                    break;
                }
            }
        }
        double winRate = (numTests2 == draw ? 0.5 : 1.0 * win / (numTests2 - draw));
        if (showDetail)
        {
            printf("%3d: %s", i, pcName[pcEnemy[i].role - ROLE_PC]);
            if (pcEnemy[i].alias.size()) printf("_%s", pcEnemy[i].alias.c_str());
            if (pcEnemy[i].lvl == -1)
            {
                printf(" Lv.?");
            }
            else
            {
                printf(" Lv.%d", pcEnemy[i].lvl);
            }
            printf(" : Win Rate : %.5lf%% (%d/%d D=%d(%.1lf%%))",
                winRate * 100, win, numTests2 - draw, draw, 100.0 * draw / numTests2);
            if (showCI)
            {
                double low, high;
                ci(win, numTests2 - draw, low, high);
                printf(" 95%% CI : [%.5lf%%, %.5lf%%]\n", low * 100, high * 100);
            }
            else
            {
                printf("\n");
            }
        }
        weight *= pcWeightA + (pcEnemy.size() > 1 ? (pcWeightB - pcWeightA) * (1.0 * i / (pcEnemy.size() - 1)) : 0.0);
        weight *= 1.0 * (numTests2 - draw) / numTests2;
        totalWinRate += winRate * weight;
        totalHpRate += (numTests2 == draw ? 0.0 : singleHpRate / (numTests2 - draw) * weight);
        totalWeight += weight;
    }
    if (totalWeight == 0.0)
    {
        totalWinRate = 0.5;
        totalHpRate = 1.0;
    }
    else
    {
        totalWinRate /= totalWeight;
        totalHpRate /= totalWeight;
    }
    if (showDetail)
    {
        printf("Average Win Rate : %.5lf%%\n", 100.0 * totalWinRate);
    }
    return AttrScore(totalWinRate, totalHpRate);
}

class AttrEval
{
public:
    virtual AttrScore eval(const AttrKey& key, bool showDetail = false) const = 0;

    virtual bool isBest(const AttrScore&) const = 0;

    virtual double getWinRate(const AttrScore& score) const
    {
        return -1;
    }

    virtual double getProfit(const AttrScore& score) const
    {
        return -1;
    }
};

class AttrEvalNpc : public AttrEval
{
public:
    virtual AttrScore eval(const AttrKey& key, bool showDetail = false) const
    {
        Player pc = myself;
        for (int i = 0; i < ATTR_COUNT; ++i) pc.attr[i] = key.at[i];
        for (int i = 0; i < 4; ++i) pc.gear[i] = gears[i][key.gi[i]];
        pc.auraSkl = key.as;
        BStat pcStat;
        preparePcBStat(pc, pcStat);
        int rseed = (AttrKeyHash()(key) & 0x3FFFFFFF) + 1;
        return calcScoreNpc(pcStat, showDetail, false, &rseed);
    }

    virtual bool isBest(const AttrScore& score) const
    {
        return score.v1 == 1.0;
    }

    virtual double getWinRate(const AttrScore& score) const
    {
        return score.v1;
    }
};

class AttrEvalPc : public AttrEval
{
public:
    virtual AttrScore eval(const AttrKey& key, bool showDetail = false) const
    {
        Player pc = myself;
        for (int i = 0; i < ATTR_COUNT; ++i) pc.attr[i] = key.at[i];
        for (int i = 0; i < 4; ++i) pc.gear[i] = gears[i][key.gi[i]];
        pc.auraSkl = key.as;
        BStat pcStat;
        preparePcBStat(pc, pcStat);
        int rseed = (AttrKeyHash()(key) & 0x3FFFFFFF) + 1;
        return calcScorePc(pcStat, showDetail, false, &rseed);
    }

    virtual bool isBest(const AttrScore& score) const
    {
        return score.v1 == 1.0;
    }

    virtual double getWinRate(const AttrScore& score) const
    {
        return score.v1;
    }
};

class AttrEvalLevel : public AttrEval
{
public:
    explicit AttrEvalLevel(int rank, int* npcBase)
    {
        mRank2 = rank * rank;
        mNpcPrefixCount = (rank + 2) / 3;
        for (int i = 0; i < NPC_COUNT_OLD2 - NPC_COUNT_OLD; ++i)
        {
            mNpcBase[i] = npcBase[i];
        }
    }

    virtual AttrScore eval(const AttrKey& key, bool showDetail = false) const
    {
        Player pc = myself;
        for (int i = 0; i < ATTR_COUNT; ++i) pc.attr[i] = key.at[i];
        for (int i = 0; i < 4; ++i) pc.gear[i] = gears[i][key.gi[i]];
        pc.auraSkl = key.as;
        BStat pcStat;
        preparePcBStat(pc, pcStat);
        int rseed = (AttrKeyHash()(key) & 0x3FFFFFFF) + 1;
        //int prefixN = prefCount[0][mNpcPrefixCount];
        int prefixN = 1;
        int numTestsFix = ((numTests - 1) / prefixN + 1) * prefixN;

        double winRate[97][NPC_COUNT_OLD2 - NPC_COUNT_OLD + 1];

        int maxi = mRank2 == 144 ? 96 : 95;
        for (int i = startLevel; i <= maxi; ++i)
        {
            winRate[i][NPC_COUNT_OLD2 - NPC_COUNT_OLD] = 0;
            double totalWeight = 0;
            for (int j = 0; j < NPC_COUNT_OLD2 - NPC_COUNT_OLD; ++j)
            {
                NonPlayer npc;
                npc.role = ROLE_NPC + NPC_COUNT_OLD + j;
                npc.lvl = mNpcBase[j] * (300 + i) / 300;
                npc.prefixCount = mNpcPrefixCount;
                npc.prefix = 0;
                BStat npcStat;
                prepareNpcBStat(npc, npcStat);
                int win = 0;
                int draw = 0;
                int numTests2 = numTestsFix;
                for (int k = 0;; ++k)
                {
                    if (ciTest == 0 && k >= numTests2) break;
                    BResult br = calcBattle(pcStat, npcStat, false, k, &rseed);
                    if (br.winner == 0) ++win;
                    else if (br.winner == 2) ++draw;
                    if (ciTest > 0 && k % prefixN == prefixN - 1)
                    {
                        double low, high;
                        ci(win + draw / 2, k + 1, low, high);
                        if (high - low < ciTest || k >= 99999999)
                        {
                            numTests2 = k + 1;
                            break;
                        }
                    }
                }
                double weight = 1.0 * (numTests2 - draw) / numTests2;
                winRate[i][j] = (numTests2 == draw ? 0.5 : 1.0 * win / (numTests2 - draw));
                winRate[i][NPC_COUNT_OLD2 - NPC_COUNT_OLD] += winRate[i][j] * weight;
                totalWeight += weight;
            }
            if (totalWeight == 0.0)
            {
                winRate[i][NPC_COUNT_OLD2 - NPC_COUNT_OLD] = 0.5;
            }
            else
            {
                winRate[i][NPC_COUNT_OLD2 - NPC_COUNT_OLD] /= totalWeight;
            }
            if (winRate[i][NPC_COUNT_OLD2 - NPC_COUNT_OLD] < 0.2)
            {
                maxi = i;
                break;
            }
        }

        AttrScore score(0, 0);
        for (int i = startLevel + 6; i <= maxi; ++i)
        {
            double tp[3][3] = {};
            double tap[3][3] = {};
            double tpo[3][3] = {};
            for (int a = 0; a <= 2; ++a)
            {
                for (int j = 0; j <= 4; ++j)
                {
                    double p = 1;
                    for (int k = 0; k < j; ++k)
                        p *= 1 - winRate[i - a - k][NPC_COUNT_OLD2 - NPC_COUNT_OLD];
                    if (j < 4) p *= winRate[i - a - j][NPC_COUNT_OLD2 - NPC_COUNT_OLD];
                    double ap = 5 * (j + 1);
                    int po = 0;
                    int s = -a - j + 4;
                    while (s > 0)
                    {
                        ap += 10.25;
                        po += mRank2 * 400 + (i + s) * (50 + mRank2);
                        s -= 3;
                    }
                    tp[a][-s] += p;
                    tap[a][-s] += ap * p;
                    tpo[a][-s] += po * p;
                }
            }
            double pp[3] = {};
            pp[0] = tp[1][0] * tp[2][0] + tp[1][2] * tp[2][0] + tp[1][0] * tp[2][1];
            pp[1] = tp[2][1] * tp[0][1] + tp[2][0] * tp[0][1] + tp[2][1] * tp[0][2];
            pp[2] = tp[0][2] * tp[1][2] + tp[0][1] * tp[1][2] + tp[0][2] * tp[1][0];
            double ppSum = pp[0] + pp[1] + pp[2];
            pp[0] /= ppSum;
            pp[1] /= ppSum;
            pp[2] /= ppSum;
            double avgAp = 0;
            double avgProfit = 0;
            for (int a = 0; a <= 2; ++a)
            {
                for (int b = 0; b <= 2; ++b)
                {
                    avgAp += pp[a] * tap[a][b];
                    avgProfit += pp[a] * tpo[a][b];
                }
            }
            avgProfit *= 100 / avgAp;
            if (avgProfit > score.v1)
            {
                score.v1 = avgProfit;
                score.v2 = i;
            }
        }
        if (showDetail)
        {
            int l1 = maxi < startLevel + 6 ? startLevel : int(score.v2) - 6;
            int l2 = maxi < startLevel + 6 ? maxi : int(score.v2);
            printf(" ");
            for (int i = 0; i < NPC_COUNT_OLD2 - NPC_COUNT_OLD; ++i)
            {
                printf("%9s", npcName[i + NPC_COUNT_OLD]);
            }
            printf("    Average\n");
            for (int i = l1; i <= l2; ++i)
            {
                printf("%02d:", i);
                for (int j = 0; j < NPC_COUNT_OLD2 - NPC_COUNT_OLD; ++j)
                {
                    printf(" %7.3lf%%", winRate[i][j] * 100.0);
                }
                printf(" %7.3lf%%\n", winRate[i][NPC_COUNT_OLD2 - NPC_COUNT_OLD] * 100.0);
            }
            printf("\n");
            if (maxi < startLevel + 6)
            {
                printf("No Profit\n");
            }
            else
            {
                printf("Average Profit(100 AP): %.3lf\n", score.v1);
                printf("Threshold Level: %d\n", int(score.v2));
            }
        }
        return score;
    }

    virtual bool isBest(const AttrScore& score) const
    {
        return false;
    }

    virtual double getProfit(const AttrScore& score) const
    {
        return score.v1;
    }

protected:
    int mRank2;
    int mNpcPrefixCount;
    int mNpcBase[NPC_COUNT_OLD2 - NPC_COUNT_OLD];
};

struct AttrEvalArgs
{
    const AttrKey* key;
    AttrScore* pScore;

    AttrEvalArgs(const AttrKey* key, AttrScore* pScore) : key(key), pScore(pScore)
    {
    }
};

const AttrEval* gpAttrEval;
std::queue<AttrEvalArgs> attrEvalTasks;
int attrEvalTaskCount;
const int attrEvalTaskCountUpperbound = 1000;
const int attrEvalTaskCountLowerbound = 500;
std::queue<std::pair<int, int> > rankTasks;
struct RankPoint
{
    explicit RankPoint(int id = 0) :
        id(id), atkRate(0), defRate(0), avgRate(0), atkWeight(0), defWeight(0)
    {
    }

    void process(int type)
    {
        if (type & 1)
        {
            if (atkWeight == 0.0)
            {
                atkRate = 50;
            }
            else
            {
                atkRate *= 100.0 / atkWeight;
            }
        }
        else
        {
            atkRate = -1;
            atkWeight = 0;
        }
        if (type & 2)
        {
            if (defWeight == 0.0)
            {
                defRate = 50;
            }
            else
            {
                defRate *= 100.0 / defWeight;
            }
        }
        else
        {
            defRate = -1;
            defWeight = 0;
        }
        if (atkWeight == 0.0 && defWeight == 0.0)
        {
            avgRate = 50;
        }
        else
        {
            avgRate = (atkRate * atkWeight + defRate * defWeight) / (atkWeight + defWeight);
        }
    }

    int id;
    double atkRate;
    double defRate;
    double avgRate;
    double atkWeight;
    double defWeight;
};
std::vector<RankPoint> rankPoints;
int rankFinishCount;

void* attrEvalWorker(void* args)
{
    pthread_mutex_lock(&threadMutex);
    ++attrEvalAliveCount;
    pthread_cond_signal(&attrEvalFinishCond);
    for (;;)
    {
        while (attrEvalWorking && attrEvalTasks.empty())
        {
            pthread_cond_wait(&attrEvalTaskCond, &threadMutex);
        }
        if (!attrEvalWorking) break;

        AttrEvalArgs evalArgs = attrEvalTasks.front();
        attrEvalTasks.pop();
        ++calcAttrCount;
        ++attrEvalWorkingCount;
        if (--attrEvalTaskCount == attrEvalTaskCountLowerbound || signalCatch)
        {
            pthread_cond_signal(&attrEvalTaskFullCond);
        }
        pthread_mutex_unlock(&threadMutex);

        *evalArgs.pScore = gpAttrEval->eval(*evalArgs.key);

        pthread_mutex_lock(&threadMutex);
        double winRate = gpAttrEval->getWinRate(*evalArgs.pScore);
        if (winRate >= 0 && winRate > bestWinRate)
        {
            bestWinRate = winRate;
        }
        double profit = gpAttrEval->getProfit(*evalArgs.pScore);
        if (profit >= 0 && profit > bestProfit)
        {
            bestProfit = profit;
        }
        --attrEvalWorkingCount;
        pthread_cond_signal(&attrEvalFinishCond);
    }
    if (--attrEvalAliveCount == 0)
    {
        pthread_cond_signal(&attrEvalFinishCond);
    }
    pthread_mutex_unlock(&threadMutex);
    pthread_exit(NULL);
    return NULL;
}

void* rankWorker(void* args)
{
    pthread_mutex_lock(&threadMutex);
    ++attrEvalAliveCount;
    int rseed = reinterpret_cast<size_t>(args);
    while (!rankTasks.empty())
    {
        std::pair<int, int> task = rankTasks.front();
        rankTasks.pop();
        pthread_mutex_unlock(&threadMutex);
        BStat attacker = (task.first < (int)pcEnemy.size() ? pcEnemyStat[task.first] : myStat);
        BStat defender = (task.second < (int)pcEnemy.size() ? pcEnemyStat[task.second] : myStat);
        int win = 0;
        int draw = 0;
        int numTests2 = numTests;
        for (int k = 0;; ++k)
        {
            if (ciTest == 0 && k >= numTests2) break;
            BResult br = calcBattle(attacker, defender, false, k, &rseed);
            if (br.winner == 0) ++win;
            else if (br.winner == 2) ++draw;
            if (ciTest > 0)
            {
                double low, high;
                ci(win + draw / 2, k + 1, low, high);
                if (high - low < ciTest || k >= 99999999)
                {
                    numTests2 = k + 1;
                    break;
                }
            }
        }
        double winRate = (numTests2 == draw ? 0.5 : 1.0 * win / (numTests2 - draw));
        double weight = 1.0 * (numTests2 - draw) / numTests2;
        pthread_mutex_lock(&threadMutex);
        rankPoints[task.first].atkRate += winRate * weight;
        rankPoints[task.first].atkWeight += weight;
        rankPoints[task.second].defRate += (1 - winRate) * weight;
        rankPoints[task.second].defWeight += weight;
        ++rankFinishCount;
        pthread_cond_signal(&attrEvalFinishCond);
    }
    if (--attrEvalAliveCount == 0)
    {
        pthread_cond_signal(&attrEvalFinishCond);
    }
    pthread_mutex_unlock(&threadMutex);
    pthread_exit(NULL);
    return NULL;
}

void* progressMeterWorker(void* args)
{
    pthread_mutex_lock(&threadMutex);
    progressMeterAlive = true;
    pthread_cond_signal(&progressMeterFinishCond);
    while (progressMeterWorking)
    {
        timeval tv2;
        gettimeofday(&tv2, NULL);
        double tvdiff = tv2.tv_sec - calcAttrTvBegin.tv_sec + (tv2.tv_usec - calcAttrTvBegin.tv_usec) / 1000000.0;
        double progress = pm.getProgress(calcAttrStage, calcAttrCount);
        printf("\rProgress: %.2lf%%", progress * 100);
        if (bestWinRate >= 0)
        {
            printf(" Best result: %.5lf%%", bestWinRate * 100);
        }
        if (bestProfit >= 0)
        {
            printf(" Best profit: %.3lf", bestProfit);
        }
        printf(" Time used: %.3lfs Estimated time: ", tvdiff);
        if (progress == 0)
        {
            printf("inf    ");
        }
        else
        {
            printf("%.3lfs   ", tvdiff / progress);
        }
        pthread_mutex_unlock(&threadMutex);
        usleep(200000);
        pthread_mutex_lock(&threadMutex);
    }
    progressMeterAlive = false;
    pthread_cond_signal(&progressMeterFinishCond);
    pthread_mutex_unlock(&threadMutex);
    pthread_exit(NULL);
    return NULL;
}

void initAuraList(int as, int s, int cost, int slot, bool* asUsed, std::vector<int>& asList)
{
    if (s == AURA_COUNT)
    {
        if (slot > 0)
        {
            for (int i = 0; i < AURA_COUNT; ++i)
            {
                if (!asUsed[i] && cost + auraCost[i] <= auraMax)
                {
                    return;
                }
            }
        }
        asList.push_back(as);
    }
    else
    {
        initAuraList(as, s + 1, cost, slot, asUsed, asList);
        if (!asUsed[s] && slot > 0 && cost + auraCost[s] <= auraMax)
        {
            asUsed[s] = true;
            initAuraList(as | 1 << s, s + 1, cost + auraCost[s], slot - 1, asUsed, asList);
            asUsed[s] = false;
        }
    }
}

void initAttrList(AttrKey& key, int s, int stepLeft, std::vector<AttrKey>& keyList)
{
    if (s < ATTR_COUNT)
    {
        int atBackup = key.at[s];
        for (; stepLeft >= 0 && key.at[s] <= maxAttr[s]; key.at[s] += initStep, --stepLeft)
        {
            initAttrList(key, s + 1, stepLeft, keyList);
        }
        key.at[s] = atBackup;
    }
    else if (stepLeft == 0)
    {
        keyList.push_back(key);
    }
}

void prepareCalcAttr()
{
    if (attrSeed.size() == 0)
    {
        std::vector<int> asList;
        bool asUsed[AURA_COUNT] = {};
        int auraCostSum = 0;
        int slot = myself.sklSlot;
        for (int i = 0; i < AURA_COUNT; ++i)
        {
            if (myself.auraSkl & 1 << i)
            {
                asUsed[i] = true;
                auraCostSum += auraCost[i];
                --slot;
            }
            if (auraFilter & 1 << i)
            {
                asUsed[i] = true;
            }
        }
        initAuraList(myself.auraSkl, 0, auraCostSum, slot, asUsed, asList);

        int giRange[4][2];
        for (int i = 0; i < 4; ++i)
        {
            if (myself.gear[i].type == GEAR_NONE && gears[i].size() > 1)
            {
                giRange[i][0] = 1;
                giRange[i][1] = gears[i].size();
            }
            else
            {
                giRange[i][0] = 0;
                giRange[i][1] = 1;
            }
        }

        int attrLeft = totalAttr;
        for (int i = 0; i < ATTR_COUNT; ++i)
        {
            attrLeft -= myself.attr[i];
        }
        initStep = attrLeft / gridSize;
        if (initStep == 0) initStep = 1;

        AttrKey key;
        int maxStep = 0;
        for (int i = 0; i < ATTR_COUNT; ++i)
        {
            key.at[i] = myself.attr[i];
            maxStep += (maxAttr[i] - key.at[i]) / initStep;
        }
        if (maxStep * initStep > attrLeft)
        {
            maxStep = attrLeft / initStep;
        }
        int attrAdd = attrLeft - maxStep * initStep;
        for (int i = 0; i < ATTR_COUNT && attrAdd > 0; ++i)
        {
            int addMax = (maxAttr[i] - key.at[i]) % initStep;
            if (addMax > attrAdd) addMax = attrAdd;
            key.at[i] += addMax;
            attrAdd -= addMax;
        }
        std::vector<AttrKey> keyList;
        initAttrList(key, 0, maxStep, keyList);

        attrSeedTotal = ((int64_t)keyList.size()) * asList.size() *
            (giRange[0][1] - giRange[0][0]) * (giRange[1][1] - giRange[1][0]) *
            (giRange[2][1] - giRange[2][0]) * (giRange[3][1] - giRange[3][0]);
        std::vector<int64_t> seedIndex;
        rseedGlobal = 1;
        if (attrSeedTotal > attrSeedMax)
        {
            seedIndex.reserve(attrSeedMax);
            std::tr1::unordered_set<int64_t> indexSet;
            for (int64_t i = attrSeedTotal - attrSeedMax + 1; i <= attrSeedTotal; ++i)
            {
                int64_t r = myrand64(&rseedGlobal, i);
                if (indexSet.insert(r).second)
                {
                    seedIndex.push_back(r);
                }
                else
                {
                    indexSet.insert(i - 1);
                    seedIndex.push_back(i - 1);
                }
            }
        }
        else
        {
            seedIndex.reserve(attrSeedTotal);
            for (int64_t i = 0; i < attrSeedTotal; ++i)
            {
                seedIndex.push_back(i);
            }
        }
        attrSeed.resize(seedIndex.size());
        for (int i = 0; i < (int)seedIndex.size(); ++i)
        {
            int j = myrand(&rseedGlobal, seedIndex.size() - i) + i;
            int64_t v = seedIndex[j];
            seedIndex[j] = seedIndex[i];
            AttrKey& k = attrSeed[i];
            k = keyList[v % keyList.size()];
            v /= keyList.size();
            for (int g = 0; g < 4; ++g)
            {
                k.gi[g] = v % (giRange[g][1] - giRange[g][0]) + giRange[g][0];
                v /= giRange[g][1] - giRange[g][0];
            }
            k.as = asList[v];
        }

        initStep = initStep * (stepRate - 1) / stepRate;
        pm.init(attrSeed.size(), initStep);
    }

    printf("Attribute seed count = ");
    if (attrSeedTotal >= 1000000000)
    {
        printf("%d%09d\n", (int)(attrSeedTotal / 1000000000), (int)(attrSeedTotal % 1000000000));
    }
    else
    {
        printf("%d\n", (int)attrSeedTotal);
    }
    if (attrSeedTotal > attrSeedMax)
    {
        printf("Attribute seed count reduced to %d(%.2lf%%)\n", attrSeedMax, 100.0 * attrSeedMax / attrSeedTotal);
    }
}

AttrPair calcAttr(const AttrEval& eval)
{
    signalCatch = false;
    signal(SIGTERM, signalHandler);
    signal(SIGINT, signalHandler);

    prepareCalcAttr();
    gpAttrEval = &eval;

    AttrMap sc;
    AttrQueue q;
    std::vector<pthread_t> threads(numThreads);
    std::vector<AttrKey> newSeed, cand, cand2;
    std::vector<AttrKey>* pSeed = &attrSeed;
    std::tr1::unordered_set<AttrKey, AttrKeyHash> seedSet;
    int step = initStep;
    timeval tv2;
    double tvdiff;

    calcAttrStage = -1;
    calcAttrCount = 0;
    bestWinRate = -1;
    bestProfit = -1;
    gettimeofday(&calcAttrTvBegin, NULL);
    attrEvalWorking = true;
    attrEvalAliveCount = 0;
    attrEvalWorkingCount = 0;
    attrEvalTaskCount = 0;
    for (int i = 0; i < numThreads; ++i)
    {
        pthread_create(&threads[i], &threadAttr, &attrEvalWorker, NULL);
    }
    pthread_mutex_lock(&threadMutex);
    while (attrEvalAliveCount < numThreads)
    {
        pthread_cond_wait(&attrEvalFinishCond, &threadMutex);
    }
    pthread_mutex_unlock(&threadMutex);
    if (verbose)
    {
        pthread_t tid;
        progressMeterWorking = true;
        progressMeterAlive = false;
        pthread_create(&tid, &threadAttr, &progressMeterWorker, NULL);
        pthread_mutex_lock(&threadMutex);
        while (!progressMeterAlive)
        {
            pthread_cond_wait(&progressMeterFinishCond, &threadMutex);
        }
        pthread_mutex_unlock(&threadMutex);
    }

    for (;;)
    {
        for (int i = 0; i < (int)pSeed->size(); ++i)
        {
            if (signalCatch) break;
            std::pair<AttrMap::iterator, bool> ir = sc.insert(AttrPair(pSeed->at(i), AttrScore()));
            if (!ir.second) continue;
            pthread_mutex_lock(&threadMutex);
            attrEvalTasks.push(AttrEvalArgs(&pSeed->at(i), &ir.first->second));
            pthread_cond_signal(&attrEvalTaskCond);
            if (++attrEvalTaskCount == attrEvalTaskCountUpperbound)
            {
                pthread_cond_wait(&attrEvalTaskFullCond, &threadMutex);
            }
            pthread_mutex_unlock(&threadMutex);
        }
        pthread_mutex_lock(&threadMutex);
        if (signalCatch)
        {
            while (attrEvalTaskCount)
            {
                attrEvalTasks.pop();
                --attrEvalTaskCount;
            }
        }
        while (attrEvalTaskCount || attrEvalWorkingCount)
        {
            pthread_cond_wait(&attrEvalFinishCond, &threadMutex);
        }
        pthread_mutex_unlock(&threadMutex);
        int queueSize = 0;
        for (int i = 0; i < (int)pSeed->size(); ++i)
        {
            AttrMap::const_iterator it = sc.find(pSeed->at(i));
            if (it == sc.end() || it->second.v1 == -1) continue;
            if (queueSize >= candidateMax)
            {
                if (AttrPairComp()(*it, q.top()))
                {
                    q.push(*it);
                    q.pop();
                }
            }
            else
            {
                q.push(*it);
                ++queueSize;
            }
        }
        cand2.clear();
        while (!q.empty())
        {
            cand2.push_back(q.top().first);
            q.pop();
        }
        if (cand == cand2)
        {
            step = step * (stepRate - 1) / stepRate;
            pthread_mutex_lock(&threadMutex);
            ++calcAttrStage;
            calcAttrCount = 0;
            pthread_mutex_unlock(&threadMutex);
        }
        else
        {
            if (cand.empty())
            {
                pthread_mutex_lock(&threadMutex);
                ++calcAttrStage;
                calcAttrCount = 0;
                pthread_mutex_unlock(&threadMutex);
            }
            cand.swap(cand2);
        }
        if (signalCatch) break;
        if (step == 0) break;
        if (eval.isBest(sc[cand.back()])) break;
        seedSet.clear();
        for (int i = 0; i < (int)cand.size(); ++i)
        {
            seedSet.insert(cand[i]);
            for (int a1 = 0; a1 < ATTR_COUNT; ++a1)
            {
                if (cand[i].at[a1] < myself.attr[a1] + step) continue;
                cand[i].at[a1] -= step;
                for (int a2 = 0; a2 < ATTR_COUNT; ++a2)
                {
                    if (a2 == a1) continue;
                    if (cand[i].at[a2] + step > maxAttr[a2]) continue;
                    cand[i].at[a2] += step;
                    seedSet.insert(cand[i]);
                    cand[i].at[a2] -= step;
                }
                cand[i].at[a1] += step;
            }
        }
        newSeed.clear();
        newSeed.reserve(seedSet.size());
        newSeed.insert(newSeed.begin(), seedSet.begin(), seedSet.end());
        pSeed = &newSeed;
    }

    pthread_mutex_lock(&threadMutex);
    attrEvalWorking = false;
    pthread_cond_broadcast(&attrEvalTaskCond);
    while (attrEvalAliveCount)
    {
        pthread_cond_wait(&attrEvalFinishCond, &threadMutex);
    }
    if (verbose)
    {
        progressMeterWorking = false;
        while (progressMeterAlive)
        {
            pthread_cond_wait(&progressMeterFinishCond, &threadMutex);
        }
    }
    pthread_mutex_unlock(&threadMutex);

    gettimeofday(&tv2, NULL);
    tvdiff = tv2.tv_sec - calcAttrTvBegin.tv_sec + (tv2.tv_usec - calcAttrTvBegin.tv_usec) / 1000000.0;
    printf("\r                                                                                              ");
    printf("\rTime used: %.3lfs\n", tvdiff);

    signal(SIGTERM, SIG_DFL);
    signal(SIGINT, SIG_DFL);

    return cand.empty() ? AttrPair() : AttrPair(*sc.find(cand.back()));
}

bool readEnemy(BStat& b)
{
    char* tok = strtok(NULL, " \n\r\t");
    if (!tok) return false;
    if (strcmp(tok, "NPC") == 0)
    {
        tok = strtok(NULL, " \n\r\t");
        if (!tok) return false;
        int x;
        if (sscanf(tok, "%d", &x) != 1 || x < 0 || x >= (int)npcEnemy.size()) return false;
        prepareNpcBStat(npcEnemy[x], b);
        return true;
    }
    else if (strcmp(tok, "PC") == 0)
    {
        tok = strtok(NULL, " \n\r\t");
        if (!tok) return false;
        if (isNumber(tok))
        {
            int x;
            if (sscanf(tok, "%d", &x) != 1 || x < 0 || x >= (int)pcEnemy.size()) return false;
            preparePcBStat(pcEnemy[x], b);
            return true;
        }
        else
        {
            for (int i = 0; i < (int)pcEnemy.size(); ++i)
            {
                if (strcmp(tok, pcEnemy[i].alias.c_str()) == 0)
                {
                    preparePcBStat(pcEnemy[i], b);
                    return true;
                }
            }
            printf("Cannot find PC with alias %s\n", tok);
        }
    }
    else
    {
        NonPlayer npc;
        if (!getNpcRolePrefix(tok, npc.role, npc.prefix)) return false;
        tok = strtok(NULL, " \n\r\t");
        if (!tok || sscanf(tok, "%d", &npc.lvl) != 1 || npc.lvl < 1) return false;
        tok = strtok(NULL, " \n\r\t");
        if (!tok || sscanf(tok, "%d", &npc.prefixCount) != 1 ||
            npc.prefixCount < 0 || npc.prefixCount > 4) return false;
        prepareNpcBStat(npc, b);
        return true;
    }
    return false;
}

int main(int argc, char* argv[])
{
    pthread_attr_init(&threadAttr);
    pthread_attr_setdetachstate(&threadAttr, PTHREAD_CREATE_DETACHED);
    setvbuf(stdout, NULL, _IONBF, 0);

    initPrefTable();
    readConfig(argc > 1 ? argv[1] : NULL);
    preparePcBStat(myself, myStat);
    npcEnemyStat.resize(npcEnemy.size());
    for (int i = 0; i < (int)npcEnemy.size(); ++i)
    {
        prepareNpcBStat(npcEnemy[i], npcEnemyStat[i]);
    }
    pcEnemyStat.resize(pcEnemy.size());
    for (int i = 0; i < (int)pcEnemy.size(); ++i)
    {
        preparePcBStat(pcEnemy[i], pcEnemyStat[i]);
    }
    showState(myStat);
    printf("\n");
    printf("Version                : %d", version / 1000);
    if (version % 1000 != 0)
    {
        printf(".%d", version % 1000 / 100);
        if (version % 100 != 0)
        {
            printf(".%d", version % 100 / 10);
            if (version % 10 != 0)
            {
                printf(".%d", version % 10);
            }
        }
    }
    printf("\n");

    char wishAmulStr[500];
    char* p = wishAmulStr;
    sprintf(p, "WISH");
    p += strlen(p);
    for (int i = 0; i < WISH_COUNT; ++i)
    {
        sprintf(p, " %d", int(myself.wish[i]));
        p += strlen(p);
    }
    sprintf(p, "\n");
    p += strlen(p);
    bool amuletEmpty = true;
    for (int i = 0; i < AMUL_COUNT; ++i)
    {
        if (myself.amul[i] > 0)
        {
            amuletEmpty = false;
            break;
        }
    }
    if (!amuletEmpty)
    {
        sprintf(p, "AMULET");
        p += strlen(p);
        for (int i = 0; i < AMUL_COUNT; ++i)
        {
            if (myself.amul[i] > 0)
            {
                sprintf(p, " %s %d", amulName[i], int(myself.amul[i]));
                p += strlen(p);
            }
        }
        sprintf(p, " ENDAMULET\n");
        p += strlen(p);
    }

    for (;;)
    {
        printf("\n");
        printf("Number of threads for calculation: %d\n", numThreads);
        if (ciTest == 0)
        {
            printf("Number of tests for win rate calculation: %d\n", numTests);
        }
        else
        {
            printf("CI threshold for win rate calculation: %lf%%\n", ciTest * 100);
        }
        printf("Start level for al calculation: %d\n", startLevel);
        printf("Reduce rate of skill/critical: %d/%d\n", reduceRateA, reduceRateB);
        printf("PC opponent weight: %d-%d\n", pcWeightA, pcWeightB);
        printf("Attribute seed max: %d\n", attrSeedMax);
        printf("Defender mode: %s\n", defMode == 0 ? "OFF" : defMode == 1 ? "ON" : "MIXED");
        printf("Verbose mode: %s\n", verbose ? "ON" : "OFF");
        printf("t <enemy> : Show details of single battle with <enemy>\n");
        printf("ti <enemy> : Same as t, but user can control SKL/CRT in each round\n");
        printf("b <enemy> : Calculate average win rate for <enemy>\n");
        printf("vt|vti|vb <enemy1> <enemy2> :\n");
        printf("    Calculate win rate or single battle between 2 enemies\n");
        printf("bnpc : Calculate win rate for all NPC in config file\n");
        printf("bpc : Calculate win rate for all PC in config file\n");
        printf("anpc : Calculate attributes for all NPC in config file\n");
        printf("apc : Calculate attributes for all PC in config file\n");
        printf("al <Rank> <SHI>:\n");
        printf("    Calculate best profit for given NPC base level\n");
        printf("rank : Calculate VS rank of all PC data and myself\n");
        printf("threads <n> : Set number of threads for calculation\n");
        printf("tests <n> : Set number of tests for win rate calculation\n");
        printf("citest <x> : Set CI threshold for win rate calculation\n");
        printf("startlevel <n> : Set start level for al calculation\n");
        printf("reducerate <a> <b> : Set reduce rate to a/b\n");
        printf("pcweight <a> <b> : Set weight range of PC opponents\n");
        printf("seedmax <n> : Set max number of attribute seeds\n");
        printf("defender [0|1|2] : Set defender mode for PvP calculation\n");
        printf("verbose [0|1] : Set verbose mode for attribute calculation\n");
        printf("q : quit\n");
        printf("<enemy> := NPC <n> | PC <n> | PC <alias> | <NPCType> <Level> <PrefixCount>\n");

        char* tok;
        for (;;)
        {
            if (!fgets(buf, sizeof(buf), stdin))
            {
                buf[0] = 'q';
                buf[1] = 0;
            }
            tok = strtok(buf, " \n\r\t");
            if (tok) break;
        }
        if (strcmp(tok, "t") == 0 || strcmp(tok, "ti") == 0)
        {
            BStat enemy;
            if (!readEnemy(enemy))
            {
                printf("Invalid enemy format\n");
                continue;
            }
            bool interact = (tok[1] == 'i');
            int counter = myrand(&rseedGlobal, auraRandCount);
            BResult br = (defMode == 1 && enemy.role >= ROLE_PC ? calcBattle(enemy, myStat, true, counter, NULL, interact) : calcBattle(myStat, enemy, true, counter, NULL, interact));
            printf("%s wins\n", br.winner == 0 ? "Attacker" : br.winner == 1 ? "Defender" : "Nobody");
        }
        else if (strcmp(tok, "vt") == 0 || strcmp(tok, "vti") == 0)
        {
            BStat enemy1, enemy2;
            if (!readEnemy(enemy1))
            {
                printf("Invalid enemy format\n");
                continue;
            }
            if (!readEnemy(enemy2))
            {
                printf("Invalid enemy format\n");
                continue;
            }
            bool interact = (tok[2] == 'i');
            int counter = myrand(&rseedGlobal, auraRandCount * auraRandCount);
            BResult br = calcBattle(enemy1, enemy2, true, counter, NULL, interact);
            printf("%s wins\n", br.winner == 0 ? "Attacker" : br.winner == 1 ? "Defender" : "Nobody");
        }
        else if (strcmp(tok, "b") == 0)
        {
            BStat enemy;
            if (!readEnemy(enemy))
            {
                printf("Invalid enemy format\n");
                continue;
            }
            int win = 0;
            int draw = 0;
            int numTests2 = numTests;
            int prefixN = 1;
            if (enemy.role < ROLE_NPC + NPC_COUNT_OLD)
            {
                int prefixCount = enemy.psvSkl % 5;
                int prefix = enemy.psvSkl / 5;
                prefixN = prefCount[prefix][prefixCount];
                numTests2 = ((numTests2 - 1) / prefixN + 1) * prefixN;
            }
            for (int i = 0;; ++i)
            {
                if (ciTest == 0 && i >= numTests2) break;
                bool defTemp = (enemy.role >= ROLE_PC && (defMode == 1 || (defMode == 2 && i & 1)));
                BResult br = (defTemp ? calcBattle(enemy, myStat, false, i) : calcBattle(myStat, enemy, false, i));
                if (br.winner == (defTemp ? 1 : 0)) ++win;
                else if (br.winner == 2) ++draw;
                if (ciTest > 0 && i % prefixN == prefixN - 1)
                {
                    double low, high;
                    ci(win + draw / 2, i + 1, low, high);
                    if (high - low < ciTest || i >= 99999999)
                    {
                        numTests2 = i + 1;
                        break;
                    }
                }
            }
            double low, high;
            ci(win, numTests2 - draw, low, high);
            printf("Win Rate : %.8lf%% (%d/%d D=%d(%.1lf%%)) 95%% CI : [%.5lf%%, %.5lf%%]\n",
                numTests2 == draw ? 50.0 : 100.0 * win / (numTests2 - draw),
                win, numTests2 - draw, draw, 100.0 * draw / numTests2,
                low * 100, high * 100);
        }
        else if (strcmp(tok, "vb") == 0)
        {
            BStat enemy1, enemy2;
            if (!readEnemy(enemy1))
            {
                printf("Invalid enemy format\n");
                continue;
            }
            if (!readEnemy(enemy2))
            {
                printf("Invalid enemy format\n");
                continue;
            }
            int win = 0;
            int draw = 0;
            int numTests2 = numTests;
            int prefixN = 1;
            if (enemy1.role < ROLE_NPC + NPC_COUNT_OLD)
            {
                int prefixCount = enemy1.psvSkl % 5;
                int prefix = enemy1.psvSkl / 5;
                prefixN *= prefCount[prefix][prefixCount] / gcd(prefixN, prefCount[prefix][prefixCount]);
            }
            if (enemy2.role < ROLE_NPC + NPC_COUNT_OLD)
            {
                int prefixCount = enemy2.psvSkl % 5;
                int prefix = enemy2.psvSkl / 5;
                prefixN *= prefCount[prefix][prefixCount] / gcd(prefixN, prefCount[prefix][prefixCount]);
            }
            if (prefixN > 1) numTests2 = ((numTests2 - 1) / prefixN + 1) * prefixN;
            for (int i = 0;; ++i)
            {
                if (ciTest == 0 && i >= numTests2) break;
                BResult br = calcBattle(enemy1, enemy2, false, i);
                if (br.winner == 0) ++win;
                else if (br.winner == 2) ++draw;
                if (ciTest > 0 && i % prefixN == prefixN - 1)
                {
                    double low, high;
                    ci(win + draw / 2, i + 1, low, high);
                    if (high - low < ciTest || i >= 99999999)
                    {
                        numTests2 = i + 1;
                        break;
                    }
                }
            }
            double low, high;
            ci(win, numTests2 - draw, low, high);
            printf("Win Rate : %.8lf%% (%d/%d D=%d(%.1lf%%)) 95%% CI : [%.5lf%%, %.5lf%%]\n",
                numTests2 == draw ? 50.0 : 100.0 * win / (numTests2 - draw),
                win, numTests2 - draw, draw, 100.0 * draw / numTests2,
                low * 100, high * 100);
        }
        else if (strcmp(tok, "bnpc") == 0)
        {
            if (npcEnemy.size() == 0)
            {
                printf("No NPC data in config file\n");
                continue;
            }
            calcScoreNpc(myStat, true, true);
        }
        else if (strcmp(tok, "bpc") == 0)
        {
            if (pcEnemy.size() == 0)
            {
                printf("No PC data in config file\n");
                continue;
            }
            if (defMode == 0 && pcDefCount == 0)
            {
                printf("No defence PC data in config file\n");
                continue;
            }
            if (defMode == 1 && pcAtkCount == 0)
            {
                printf("No attack PC data in config file\n");
                continue;
            }
            calcScorePc(myStat, true, true);
        }
        else if (strcmp(tok, "anpc") == 0)
        {
            if (npcEnemy.size() == 0)
            {
                printf("No NPC data in config file\n");
                continue;
            }
            AttrEvalNpc evalNpc;
            AttrPair ap = calcAttr(evalNpc);
            if (signalCatch)
            {
                printf("Calculation Interrupted\n");
            }
            if (ap.second.v1 == -1)
            {
                printf("No Result\n");
            }
            else
            {
                printf("Attribute Result:\n");
                printf("%s", pcName[myself.role - ROLE_PC]);
                if ((myself.role == ROLE_WU || myself.role == ROLE_XI || myself.role == ROLE_XIA) && myself.growth > 0) printf(" G=%d", myself.growth);
                printf(" %d %d %d %d\n", myself.lvl, myself.kfLvl, myself.sklSlot, myself.quality);
                printf("%s", wishAmulStr);
                ap.first.print();
                printf("\n");
                evalNpc.eval(ap.first, true);
            }
        }
        else if (strcmp(tok, "apc") == 0)
        {
            if (pcEnemy.size() == 0)
            {
                printf("No PC data in config file\n");
                continue;
            }
            if (defMode == 0 && pcDefCount == 0)
            {
                printf("No defence PC data in config file\n");
                continue;
            }
            if (defMode == 1 && pcAtkCount == 0)
            {
                printf("No attack PC data in config file\n");
                continue;
            }
            AttrEvalPc evalPc;
            AttrPair ap = calcAttr(evalPc);
            if (signalCatch)
            {
                printf("Calculation Interrupted\n");
            }
            if (ap.second.v1 == -1)
            {
                printf("No Result\n");
            }
            else
            {
                printf("Attribute Result:\n");
                printf("%s", pcName[myself.role - ROLE_PC]);
                if ((myself.role == ROLE_WU || myself.role == ROLE_XI || myself.role == ROLE_XIA) && myself.growth > 0) printf(" G=%d", myself.growth);
                printf(" %d %d %d %d\n", myself.lvl, myself.kfLvl, myself.sklSlot, myself.quality);
                printf("%s", wishAmulStr);
                ap.first.print();
                printf("\n");
                evalPc.eval(ap.first, true);
            }
        }
        else if (strcmp(tok, "rank") == 0)
        {
            if (pcEnemy.size() == 0)
            {
                printf("No PC data in config file\n");
                continue;
            }
            rankPoints.clear();
            while (!rankTasks.empty()) rankTasks.pop();
            int totalCount = pcAtkCount * pcDefCount + pcEnemy.size();
            rankFinishCount = 0;
            for (int i = 0; i <= (int)pcEnemy.size(); ++i)
            {
                rankPoints.push_back(RankPoint(i));
            }
            for (int i = 0; i <= (int)pcEnemy.size(); ++i)
            {
                if (i < (int)pcEnemy.size() && pcEnemy[i].type == 2) continue;
                for (int j = 0; j <= (int)pcEnemy.size(); ++j)
                {
                    if (j == i) continue;
                    if (j < (int)pcEnemy.size() && pcEnemy[j].type == 1) continue;
                    rankTasks.push(std::pair<int, int>(i, j));
                }
            }

            std::vector<pthread_t> threads(numThreads);
            myrand(&rseedGlobal, 1);
            for (int i = 0; i < numThreads; ++i)
            {
                pthread_create(&threads[i], &threadAttr, &rankWorker, reinterpret_cast<void*>(rseedGlobal));
            }
            pthread_mutex_lock(&threadMutex);
            while (!rankTasks.empty() || attrEvalAliveCount > 0)
            {
                if (verbose) printf("\rProgress: %.2lf%%    ", 100.0 * rankFinishCount / totalCount);
                pthread_cond_wait(&attrEvalFinishCond, &threadMutex);
            }
            if (verbose) printf("\r                              \r");
            pthread_mutex_unlock(&threadMutex);
            for (int i = 0; i <= (int)pcEnemy.size(); ++i)
            {
                rankPoints[i].process(i == (int)pcEnemy.size() ? 3 : pcEnemy[i].type);
            }
            for (int i = 0; i <= (int)pcEnemy.size(); ++i)
            {
                for (int j = i + 1; j <= (int)pcEnemy.size(); ++j)
                {
                    if (rankPoints[i].avgRate < rankPoints[j].avgRate)
                    {
                        std::swap(rankPoints[i], rankPoints[j]);
                    }
                }
                printf("%3d:%7.3lf%% (", i + 1, rankPoints[i].avgRate);
                if (rankPoints[i].atkRate == -1)
                {
                    printf("ATK: --.---%% ");
                }
                else
                {
                    printf("ATK:%7.3lf%% ", rankPoints[i].atkRate);
                }
                if (rankPoints[i].defRate == -1)
                {
                    printf("DEF: --.---%%) ");
                }
                else
                {
                    printf("DEF:%7.3lf%%) ", rankPoints[i].defRate);
                }
                if (rankPoints[i].id < (int)pcEnemy.size())
                {
                    printf("%s", pcName[pcEnemy[rankPoints[i].id].role - ROLE_PC]);
                    if (pcEnemy[rankPoints[i].id].alias.size()) printf("_%s", pcEnemy[rankPoints[i].id].alias.c_str());
                }
                else
                {
                    printf("Myself");
                }
                printf("\n");
            }
        }
        else if (strcmp(tok, "al") == 0)
        {
            int rank = 0;
            if ((tok = strtok(NULL, " \n\r\t")) == NULL ||
                (strcmp(tok, "C") == 0 ? rank = 1 :
                    strcmp(tok, "CC") == 0 ? rank = 2 :
                    strcmp(tok, "CCC") == 0 ? rank = 3 :
                    strcmp(tok, "B") == 0 ? rank = 4 :
                    strcmp(tok, "BB") == 0 ? rank = 5 :
                    strcmp(tok, "BBB") == 0 ? rank = 6 :
                    strcmp(tok, "A") == 0 ? rank = 7 :
                    strcmp(tok, "AA") == 0 ? rank = 8 :
                    strcmp(tok, "AAA") == 0 ? rank = 9 :
                    strcmp(tok, "S") == 0 ? rank = 10 :
                    strcmp(tok, "SS") == 0 ? rank = 11 :
                    strcmp(tok, "SSS") == 0 ? rank = 12 : 0) == 0)
            {
                printf("Invalid parameters\n");
                continue;
            }
            int base[NPC_COUNT_OLD2 - NPC_COUNT_OLD];
            bool flag = true;
            for (int i = 0; i < NPC_COUNT_OLD2 - NPC_COUNT_OLD; ++i)
            {
                if ((tok = strtok(NULL, " \n\r\t")) == NULL ||
                    sscanf(tok, "%d", &base[i]) != 1 || base[i] < 1 || base[i] > 4000)
                {
                    flag = false;
                    break;
                }
            }
            if (!flag)
            {
                printf("Invalid parameters\n");
                continue;
            }
            AttrEvalLevel evalLevel(rank, base);
            AttrPair ap = calcAttr(evalLevel);
            if (signalCatch)
            {
                printf("Calculation Interrupted\n");
            }
            if (ap.second.v1 == -1)
            {
                printf("No Result\n");
            }
            else
            {
                printf("Attribute Result:\n");
                printf("%s", pcName[myself.role - ROLE_PC]);
                if ((myself.role == ROLE_WU || myself.role == ROLE_XI || myself.role == ROLE_XIA) && myself.growth > 0) printf(" G=%d", myself.growth);
                printf(" %d %d %d %d\n", myself.lvl, myself.kfLvl, myself.sklSlot, myself.quality);
                printf("%s", wishAmulStr);
                ap.first.print();
                printf("\n");
                evalLevel.eval(ap.first, true);
            }
        }
        else if (strcmp(tok, "threads") == 0)
        {
            int n = 0;
            if ((tok = strtok(NULL, " \n\r\t")) == NULL ||
                sscanf(tok, "%d", &n) != 1 || n < 1)
            {
                printf("Invalid parameter\n");
                continue;
            }
            if (n > 64)
            {
                printf("Too many threads\n");
                continue;
            }
            numThreads = n;
        }
        else if (strcmp(tok, "tests") == 0)
        {
            int n = 0;
            if ((tok = strtok(NULL, " \n\r\t")) == NULL ||
                sscanf(tok, "%d", &n) != 1 || n < 1 || n > 100000000)
            {
                printf("Invalid parameter\n");
                continue;
            }
            numTests = n;
        }
        else if (strcmp(tok, "citest") == 0)
        {
            double x = 0;
            if ((tok = strtok(NULL, " \n\r\t")) == NULL ||
                sscanf(tok, "%lf", &x) != 1 || x < 0 || x > 100)
            {
                printf("Invalid parameter\n");
                continue;
            }
            ciTest = x / 100;
        }
        else if (strcmp(tok, "startlevel") == 0)
        {
            int n = 0;
            if ((tok = strtok(NULL, " \n\r\t")) == NULL ||
                sscanf(tok, "%d", &n) != 1 || n < 0 || n > 88)
            {
                printf("Invalid parameter\n");
                continue;
            }
            startLevel = n;
        }
        else if (strcmp(tok, "reducerate") == 0)
        {
            int a = 0, b = 0;
            if ((tok = strtok(NULL, " \n\r\t")) == NULL ||
                sscanf(tok, "%d", &a) != 1 ||
                (tok = strtok(NULL, " \n\r\t")) == NULL ||
                sscanf(tok, "%d", &b) != 1 ||
                a < 0 || b < 1 || a > b)
            {
                printf("Invalid parameter\n");
                continue;
            }
            reduceRateA = a;
            reduceRateB = b;
        }
        else if (strcmp(tok, "pcweight") == 0)
        {
            int a = 0, b = 0;
            if ((tok = strtok(NULL, " \n\r\t")) == NULL ||
                sscanf(tok, "%d", &a) != 1 ||
                (tok = strtok(NULL, " \n\r\t")) == NULL ||
                sscanf(tok, "%d", &b) != 1 ||
                a < 1 || b < 1)
            {
                printf("Invalid parameter\n");
                continue;
            }
            pcWeightA = a;
            pcWeightB = b;
        }
        else if (strcmp(tok, "seedmax") == 0)
        {
            int n = 0;
            if ((tok = strtok(NULL, " \n\r\t")) == NULL ||
                sscanf(tok, "%d", &n) != 1 || n < 1 || n > 100000000)
            {
                printf("Invalid parameter\n");
                continue;
            }
            attrSeedMax = n;
            attrSeed.clear();
        }
        else if (strcmp(tok, "defender") == 0)
        {
            if ((tok = strtok(NULL, " \n\r\t")) != NULL)
            {
                int x;
                if (sscanf(tok, "%d", &x) != 1 || x < 0 || x > 2)
                {
                    printf("Invalid parameter\n");
                    continue;
                }
                defMode = x;
            }
            else
            {
                defMode = (defMode + 1) % 3;
            }
        }
        else if (strcmp(tok, "verbose") == 0)
        {
            if ((tok = strtok(NULL, " \n\r\t")) != NULL)
            {
                int x;
                if (sscanf(tok, "%d", &x) != 1 || x < 0 || x > 1)
                {
                    printf("Invalid parameter\n");
                    continue;
                }
                verbose = x;
            }
            else
            {
                verbose = !verbose;
            }
        }
        else if (strcmp(tok, "debug") == 0)
        {
            debug = !debug;
        }
        else if (strcmp(tok, "q") == 0)
        {
            break;
        }
        else
        {
            printf("Invalid command : \"%s\"\n", tok);
        }
    }

    return 0;
}


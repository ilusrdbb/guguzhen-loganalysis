# guguzhen-loganalysis

自用咕咕镇战斗记录转计算器PC数据工具

**由于目前不分析具体的战斗记录只是脑补对面的装备，会与实际产生较大的误差，只建议不在乎出击胜率的懒人使用**

本项目基于pycharm开发，建议环境python 3.9，并需要安装lxml

使用方法：

编辑咕咕镇剩余价值收割机脚本，在232行dbInit()下添加如下代码并保存
```
    var b = new Array();
    db.battleLog
        .each(function(a){
            b.push(a);
        });
    console.log(b);
```
f12开启控制台，刷新咕咕镇网页，找到刚才打印的Array，右键选复制Object，粘贴至项目source目录下的1.txt中

最后根据自身需求修改config.py配置，运行main.py，会在项目source目录下生成pc.txt文件

Q:我想加xxx功能

A:自用工具，请勿提出需求，没空搞，但是如果发现bug欢迎提交issue

Q:为啥读取战斗记录要这么麻烦

A:本人水平有限，尝试过python直接读取chrome的indexeddb一直不行，如果有好的读取办法欢迎提出非常感谢

Q:写的啥玩意，什么垃圾代码

A:python没咋学过，这很正常，你骂的对

Q:**垃圾游戏早退坑早解脱**

A:附议

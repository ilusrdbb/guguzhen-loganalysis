# guguzhen-loganalysis

自用咕咕镇战斗记录转计算器PC数据工具

由于目前不分析具体的战斗记录只是脑补对面的装备，会与实际产生较大的误差，只建议不在乎出击胜率的懒人使用

本项目基于pycharm开发，建议环境python 3.9，并根据requirements安装依赖

关于压缩包内计算器的说明:

武器 彩金对剑 COLORFUL 

天赋 不动如山 SHAN

樱桃 全属性 AAA 暴击抵抗 CRTR 技能抵抗 SKLR

卡片雅名称YA，用M=指定雅的模式 0白天1黑夜2凶神，表示凶神雅例子 YA M=2 850 1100 7 11

使用方法：

解压release的压缩包，由于进攻防御等级的存在，暂时需要配合压缩包内的计算器使用

更新最新的咕咕镇剩余价值收割机脚本，点击咕咕镇页面左侧脚本下拉处的导出历史按钮（PS：欢迎提供给我历史文件以测试），将文件复制到项目source目录中

如果有多个号将多个导出历史文件一并复制进解压后的source目录中（文件名不能为pc.txt），程序运行后会自动整合多个文件的记录

最后根据自身需求修改config.yaml配置，运行main.exe，会在source目录下生成pc.txt文件

注意，通过主题插件自定义装备图片的情况下程序无法获取装备品质，此时默认对手全为非红装，请尽量使用插件默认主题或不使用插件

最后，感谢五神、熊大、Mulexe为本项目提供建议与测试数据

Q:我想加xxx功能

A:自用工具，请勿提出需求，没空搞，但是如果发现bug欢迎提交issue

Q:写的啥玩意，什么垃圾代码

A:python没咋学过，这很正常，你骂的对

Q:**垃圾游戏早退坑早解脱**

A:附议

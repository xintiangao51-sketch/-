MDK D2R MOD说明文件
更新日期：2021年12月08日

有什么建议可以在凯恩之角给我留言或者私信，或者BN上给我留言也可以，也欢迎来基，开车带小号打个6BOSS啥的；
我的BN ID：ZhangMDKRU#2129

或者在QQ群里留言吧，BN上回答十分不方便，文字屏蔽还不能发图。
1群名称：D2R MOD交流群
群   号：1011030151  （已满，会逐渐删除不说话的群友）

2群名称：D2R MOD交流群2群
群   号：785793674  （1群满的情况下请加这个）

使用方式：

解压到D2R游戏目录里，最终目录应该是这样的：
游戏目录\mods\MDK\MDK.mpq\data...

然后d2r.exe建个快捷方式，快捷方式加下面的参数，注意-mod前面有空格
 -mod MDK -txt
若想直接用窗口模式启动游戏，可以加上-w参数，最终参数如下
 -mod MDK -txt -w
战网程序设置内，填写到额外命令行那一栏里，即可用战网启动MOD。


***重要提示***
旧版由于有掉落物品显示文字超量导致崩溃的bug
所以请使用本MOD的朋友们及时更新2021.11.24版本MOD文件。
如果发现新的崩溃情况，请及时跟我联系。


***重要提示2***
为了方便大家自己按照自己的意愿来编辑文本，1126版开始将常用编辑的部分统一放到了item-gems文件中
可以通过设置器直接打开该文件，然后按照自己的意思去编辑其中的内容，zhTW后面的文字就是繁中默认显示的文字
其中箭矢、药瓶、宝石等都可以很快地找到位置，如果不喜欢MOD自带的风格，就按照自己的意思去编辑吧。

如果编辑后游戏崩溃无法打开，可以用设置器一键恢复文本设置而不修改其他设置。


另外，最近时间有限，可能不会频繁更新mod，mod也趋向于稳定，大多是修复bug等更新
mod是开放式，而且把自定义的部分内容统一集中到了item-gems.json文件中，大家自行修改这一个文件就能自定义大多数内容


更新内容：
----------------------------------------------

2021.12.08 第二次更新：
1、修复了设置器代码错误导致无法生成names文件的问题
2、设置器增加了装备名字无染色和部分染色的选项
3、增加重点迷宫的入口光柱提示，光柱存在于目标四周125码的范围，超出范围会因程序优化而消除
4、增加地图交互物品如宝箱等的发光提示
5、引导光柱和宝箱发光可以通过设置器开启或者关闭
6、牛王模型增大，遗忘骑士和尼拉塞克模型略微增大

2021.12.08更新：
1、修复一些已知的问题
2、修复了手柄UI缩放无效的问题（请彻底删除旧MOD然后重装生效）
3、修复方盒辅助框内升级公式无效的问题
4、统一改成了重制版的装备翻译，部分底材名称差异较大的会提示两个名称
5、进一步精简显示，并制作成无染色与部分染色两个版本（这也是各版MOD趋同进化的结果？）
6、以上面的重构为基础，修复了部分套装的套组缺失提示
7、无形装备改为深绿色显示，原深绿色显示的【超强】变为粉色，四种劣质均为缩写的红色

2021.12.05更新：
1、正式匹配了2.3版本暗黑2重制版，修复了已知的问题
2、增加了在任务界面查看塔拉夏古墓图标位置的功能
3、各项神坛增加了功能说明
4、任务界面说明内容修改，更加直观
5、提供了“显示吐槽”与“不显示吐槽”的设置开关
6、无论如何，尽管我反复测试，但还是要说——丢装备前把房间名截个图，万一中招，删掉MOD马上回去捡
7、“粗制的”缩写为[粗]了，四个劣质前缀均加上红色区分开
8、设置器提供更多的自定义设置选项，可以自行设置包括金币颜色、删除劣质前缀等
9、1群满了，请加2群





实际效果：
结合了凯恩之角的各种MOD，并按照个人习惯有所细微调整。
1、结合了吐槽内容，可以给新手一些直观提示
2、结合了符文编号、装备变量上限显示，繁体中文、简体中文、英文三种语言有效
3、护身符、戒指、项链、珠宝等增加英文提示，部分精英装备附带英文名字
4、掉落物品光柱效果：
	a、戒指、项链、珠宝  》 光柱+感叹号
	b、大中小护身符、无暇与完美宝石  》 光柱+套装发光
	c、19#以上高等级符文  》 光柱+闪电+圣光弹
	d、15#-18#符文 》 光柱
	e、20#以上高等级符文有地面闪光定位
5、危险怪物提示
	a、冥河娃娃头上增加 △ 塔拉夏符文标识
	b、牛头人头上增加 下箭头 塔拉夏符文标识
	c、电鬼头上增加 十 塔拉夏符文标识
	d、遗忘骑士增加符文标识
	e、蛇魔法师增加符文标识
	f、牛王、尼拉塞克、衣卒尔增加符文标识
	g、安达利尔增加符文标识与赫拉迪克光柱（目的在于凸显K6 BOSS的莉莉丝）
6、地图等级提示，罗格营地的等级就是牛关等级
7、精英级装备用紫色单独提示，盾牌与盔甲提示轻中重等
8、在经验条下方的功能按键上增加符文之语、合成公式、85级场景、FCR表等的速查
9、打开赫拉迪克方盒时增加合成公式提示框（更新两个不同版本）
10、增加底材白装的单独提示
11、6BOSS钥匙、高等符文使用D3的传奇掉落声音
12、使用文件夹的mod加载方式，方便其他朋友在此基础上的修改和自定义
13、超强的装备单独颜色提示
14、提供了牛场屏蔽版、新手屏蔽版（就是屏蔽小药瓶、卷轴、箭矢等）和无屏蔽版三种不同配置
15、提供自定义设置程序，可进行傻瓜化自定义设置
16、按H键进入帮助页面，可以看到各种FCR表、合成表等速查资料
17、特别定制的血条风格与怪物技能色彩
18、无形物品显示为青色（全新的颜色）


***重要提示***
MOD封包默认状态（也是可设置项）：
1、加大字体尺寸
2、全咒符、项链、戒指有光柱
3、15#以上符文有光柱
4、无暇完美宝石有光柱
5、带编号符文
6、默认方盒风格
7、哥特风格血条
8、牛场屏蔽规则
9、杂物仅显示图标
10、彩色技能图标
11、准圆字体
12、圆形超大血瓶
13、显示杂物图标




以前的更新内容
----------------------------------

2021.12.02更新：
1、昨天太困了没有测试就压包了，有很多问题，今天逐个解决
2、修复UI位移，冰增加尺寸设置，可自选100%、85%、75%，自己修改文件还有65%的注释
3、修复使用彩色词条导致丢失字符串的问题
4、恢复红蓝紫药瓶的默认颜色为白色
5、修复钻石图标会被强制染色的问题
6、修复黄色与蓝色装备有时候前后缀颜色变色的问题
7、对于隐藏的“劣等”“损坏”“破旧”的劣等前缀使用了红色与褐色凸显，并且取消隐藏词缀
8、主要还是减少文字量修复丢装备在地上导致崩溃的问题


2021.12.01更新：
1、收到多个暗金装备落地导致崩溃的BUG，还是文字超量的问题
2、为了从根本上解决文字超量的崩溃bug，暂时删去吐槽内容，同时调整底材内容显示，压缩文字量
3、增加彩色装备属性词条，可以从设置器打开该选项
4、无形装备地面显示颜色调整，药瓶颜色调整
5、更改设置器的设置方式与判断逻辑
6、加大高等符文掉落的模型，可以很明显的看到掉落的符文在哪，和地面标定闪光双重保险


2021.11.28更新：
1、收到方盒辅助框的公式错误，与帮助界面同出一辙，紧急修正
2、调整了底材提示的内容，增加提示任务打孔数量，显示为“任4”等字（暂定测试效果）
3、调整红药瓶颜色


2021.11.28更新：
1、修复了帮助界面的公式错误（梅开二度了，天国的28#），我重新核对了一下公式表，这次没错误了
       a>顺便发现了“踩蘑菇”那个网站里的符文之语搜索器中“幽暗 Gloom”的公式错了，19#写成了15#
2、修复了盒子内辅助框的公式错误，更新辅助框版本为2.05
3、制作了非图标版本的文件，现在可以选择不要图标了
4、将繁体字体和简体字体文件统一，均使用blizzardglobal-v5_81.ttf
5、将无形物品颜色改为青色（暂定测试效果）
6、金币颜色改回白色，金色与暗金物品太靠色，会影响对暗金色的注意力
7、6BOSS KEY与24#以上的高等符文声音增加派蒙的语音
8、20#以上符文增加地面闪光提示，别再说找不到了
9、修复三个繁体字显示*的问题
10、增加隶变字体可选择
11、增加安达利尔的标定与光柱（魔母巢穴太暗了，神说要有光）
12、增加蛇魔法师的标定，采用最小的半圆符文标定，为了区分开其他标定怪物，目的是标定尼拉塞克的bug蛇，
       但第二幕第三幕第五幕的蛇魔法师就都有了标定，暂时先标上，看反应决定去留。
13、修改底材提示的显示方式，减少一行
14、提供了金色传说等几个可替换音频供替换高等符文掉落音
2021.11.26更新：
1、修复了帮助界面的公式错误，恢复帮助界面
2、使用更加完整的图标，初步将常用非装备类物品加上图标
3、牛场规则同时将低级符文的名称缩写为图标+编号，小物品、宝石等直接用图标显示
4、超红和超蓝更换了图片，更好分辨
5、添加了彩色技能图标，可以用设置程序选择
6、采用了全新的设置程序判断方式，设置程序必须使用1126.1或更新版才能正常工作
7、将大部分会自定义的内容统一放置到item-gems文件中方便编辑，可以通过设置器直接打开这个文件
8、屏蔽规则和图标规则分离，可以独立选择，屏蔽规则主要作用于装备屏蔽，图标规则作用于非装备物品
9、设置程序增加重置文本功能，当自己编辑文本导致系统出bug，可以一件恢复到MOD默认文本状态

2021.11.24更新：
1、发现了圣堂武士的力量铠甲丢地上会崩溃的情况，吐槽文字太多进行简化
2、为了减少文字量，将“精英”改为“精”，去除变量前面的“MAX:”
3、发现帮助界面背景里CTA组合符文写错了，11#写成了15#，于是去掉了神符之语背景
4、增加了高等符文掉落时的落雷特效，等级越高落雷越猛
5、对固定血条增加设置选项，固定血条增加了背景框
6、尝试将血瓶改为图标形式，觉得不习惯可以自己先改回来
7、咒符掉落后的特效标识由感叹号变为巴尔光环
8、6BOSS钥匙掉落后增加冰球特效
9、去除屏蔽模式里的黑条

2021.11.23更新：
1、提供了正式的批处理设置程序，请在D2R目录下运行进行自定义设置（注意不是mods目录下）
2、将佣兵图标鼠标延时激活的时间改为3秒（视情况再增加吧）
3、增加符文之语英文版的变量显示
4、加大了符文的显示框，真的很大了（视情况搞个设置）
5、提供了牛场屏蔽版、新手屏蔽版（就是屏蔽小药瓶、卷轴、箭矢等）和无屏蔽版三种，可在设置中自己设置
6、附加了MCMod中的实用主义版赫拉迪克方盒界面，可在设置中设置
7、之前的小批处理设置都统一到正式的设置程序中
8、整合了帮助页面的修改程序，将速查资料全部放入了帮助页面内
9、帮助页面还能放啥内容大家帮忙想想

2021.11.22更新：
1、确定了恶性BUG是由于掉落地面的物品显示文字数量超出上限所致，不光是执政官铠甲强制，还找到了另外几个也会崩溃的情况，例如神秘之斧眼光等
2、为了结局恶性BUG，在有吐槽内容的情况下，删掉了英文名称只保留中文名称，现已知的会崩溃的符文之语组合已经没有影响了。

2021.11.21更新：
1、11.19与11.20版有一个恶性BUG，就是使用执政官铠甲制作符文之语“强制”之后，将铠甲丢到地上会导致游戏崩溃。
经过反复测试排除，应该是名称过长导致，但具体的原因不明。
于是将执政官铠甲关于底材的提示部分颜色代码删除解决。（其实删除其他内容也可以，就是减少三个字就可以）
所以请使用本MOD的朋友们及时更新MOD文件。
2、将牛王、尼拉塞克、衣卒尔进行了符文标识。
3、将遗忘骑士进行了符文标识，方便（冰法）打超市。（就是混沌避难所里冰免的骷髅骑士法师，同理西希之王也会被标识）
     该功能原本是想标识三个封印BOSS，但由于封印BOSS并没有独立的配置文件，所以退而求其次标识遗忘骑士（西希之王）。
     如果有大佬找到了能准确标识暗金怪的方法，还望不吝赐教。
4、尝试将部分金怪名字加上英文，目的是拉长血条显示使之能更明显看到血条变化。（不知意义如何，K6BOSS时有点用）
5、整合了凯恩之角里新的方盒配方MOD，可以隐藏提示框的版本。
6、增加自定义配置程序
	a、恢复原版符文
	b、恢复原版字体大小
7、调整FCR表的位置到【跑步】按钮上，其他速查表全部使用不会重复引用的功能图标。
----------------------------------------------
2021.11.20更新
1、FCR/FHR表因为填错空导致未能显示，重新填写，已经可以速查。
2、危险怪物提示由NPC感叹号改为塔拉夏符文，牛头为双箭头、冥河娃娃为三角形、电鬼为十字花；
     这样与掉落物品的感叹号区分开。
3、提供简单的自定义配置程序
	a、去除戒指光柱
	b、去除项链光柱
	c、增加所有等级宝石光柱
	d、增加所有等级符文光柱



文件解构示意：
└─MDK.mpq
    │  (listfile)
    │  modinfo.json  版本记录
    │  
    └─data
        ├─global
        │  ├─excel
        │  │      misc.txt  6BOSS钥匙图片文件定义
        │  │      sounds.txt  传奇掉落声音文件定义
        │  │      
        │  └─ui
        │      └─layouts
        │              hireablespanelhd.json  移动佣兵框位置
        │              horadriccubelayouthd.json  增加赫拉迪克方块参考公式框
        │              _profileasian.json
        │              _profilehd.json  清除黑色小空格
        │              
        ├─hd
        │  ├─character
        │  │  └─enemy
        │  │          bonefetish1.json  冥河娃娃加感叹号
        │  │          bloodlord1.json  鲜血之王、死族首领牛头人加感叹号
        │  │          willowisp1.json  电鬼加感叹号
        │  │          fallen1_test.json  第一幕出门沉沦魔配置文件，用于测试（加_test后对游戏无实际作用）
        │  │          quillrat1_test.json  第一幕出门针刺鼠配置文件，用于测试（加_test后对游戏无实际作用）
        │  │          zombie1_test.json  第一幕出门僵尸配置文件，用于测试（加_test后对游戏无实际作用）
        │  │          
        │  ├─global
        │  │  ├─sfx
        │  │  │  └─item
        │  │  │          @soundExample.txt  音效定义文件
        │  │  │          high_rune.flac  传奇掉落声音文件
        │  │  │          torch_key.flac  传奇掉落声音文件
        │  │  │          
        │  │  ├─ui
        │  │  │  └─items
        │  │  │      └─misc
        │  │  │          ├─key  修改6BOSS钥匙图片
        │  │  │          │      countess_key.lowend.sprite
        │  │  │          │      countess_key.sprite
        │  │  │          │      nihlathak_key.lowend.sprite
        │  │  │          │      nihlathak_key.sprite
        │  │  │          │      summoner_key.lowend.sprite
        │  │  │          │      summoner_key.sprite
        │  │  │          │      
        │  │  │          └─rune  修改全部符文图片，增加符文编号
        │  │  │                  amn_rune.lowend.sprite
        │  │  │                  amn_rune.sprite
        │  │  │                  ber_rune.lowend.sprite
        │  │  │                  ber_rune.sprite
        │  │  │                  cham_rune.lowend.sprite
        │  │  │                  cham_rune.sprite
        │  │  │                  dol_rune.lowend.sprite
        │  │  │                  dol_rune.sprite
        │  │  │                  eld_rune.lowend.sprite
        │  │  │                  eld_rune.sprite
        │  │  │                  el_rune.lowend.sprite
        │  │  │                  el_rune.sprite
        │  │  │                  eth_rune.lowend.sprite
        │  │  │                  eth_rune.sprite
        │  │  │                  fal_rune.lowend.sprite
        │  │  │                  fal_rune.sprite
        │  │  │                  gul_rune.lowend.sprite
        │  │  │                  gul_rune.sprite
        │  │  │                  hel_rune.lowend.sprite
        │  │  │                  hel_rune.sprite
        │  │  │                  io_rune.lowend.sprite
        │  │  │                  io_rune.sprite
        │  │  │                  ist_rune.lowend.sprite
        │  │  │                  ist_rune.sprite
        │  │  │                  ith_rune.lowend.sprite
        │  │  │                  ith_rune.sprite
        │  │  │                  jah_rune.lowend.sprite
        │  │  │                  jah_rune.sprite
        │  │  │                  ko_rune.lowend.sprite
        │  │  │                  ko_rune.sprite
        │  │  │                  lem_rune.lowend.sprite
        │  │  │                  lem_rune.sprite
        │  │  │                  lo_rune.lowend.sprite
        │  │  │                  lo_rune.sprite
        │  │  │                  lum_rune.lowend.sprite
        │  │  │                  lum_rune.sprite
        │  │  │                  mal_rune.lowend.sprite
        │  │  │                  mal_rune.sprite
        │  │  │                  nef_rune.lowend.sprite
        │  │  │                  nef_rune.sprite
        │  │  │                  ohm_rune.lowend.sprite
        │  │  │                  ohm_rune.sprite
        │  │  │                  ort_rune.lowend.sprite
        │  │  │                  ort_rune.sprite
        │  │  │                  pul_rune.lowend.sprite
        │  │  │                  pul_rune.sprite
        │  │  │                  ral_rune.lowend.sprite
        │  │  │                  ral_rune.sprite
        │  │  │                  shael_rune.lowend.sprite
        │  │  │                  shael_rune.sprite
        │  │  │                  sol_rune.lowend.sprite
        │  │  │                  sol_rune.sprite
        │  │  │                  sur_rune.lowend.sprite
        │  │  │                  sur_rune.sprite
        │  │  │                  tal_rune.lowend.sprite
        │  │  │                  tal_rune.sprite
        │  │  │                  thul_rune.lowend.sprite
        │  │  │                  thul_rune.sprite
        │  │  │                  tir_rune.lowend.sprite
        │  │  │                  tir_rune.sprite
        │  │  │                  um_rune.lowend.sprite
        │  │  │                  um_rune.sprite
        │  │  │                  vex_rune.lowend.sprite
        │  │  │                  vex_rune.sprite
        │  │  │                  zod_rune.lowend.sprite
        │  │  │                  zod_rune.sprite
        │  │  │                  
        │  │  └─video
        │  │          blizzardlogos.webm  跳过开始动画
        │  │          logoanim.webm  跳过开始动画
        │  │          
        │  ├─items
        │  │  │  items.json  物品简写定义
        │  │  │  
        │  │  └─misc
        │  │      ├─amulet  项链光柱特效
        │  │      │      amulet.json
        │  │      │      viper_amulet.json
        │  │      │      
        │  │      ├─charm  护身符光柱特效
        │  │      │      charm_large.json
        │  │      │      charm_medium.json
        │  │      │      charm_small.json
        │  │      │      
        │  │      ├─gem  无暇、完美宝石光柱特效
        │  │      │      flawless_amethyst.json
        │  │      │      flawless_diamond.json
        │  │      │      flawless_emerald.json
        │  │      │      flawless_ruby.json
        │  │      │      flawless_saphire.json
        │  │      │      flawless_skull.json
        │  │      │      flawless_topaz.json
        │  │      │      perfect_amethyst.json
        │  │      │      perfect_diamond.json
        │  │      │      perfect_emerald.json
        │  │      │      perfect_ruby.json
        │  │      │      perfect_saphire.json
        │  │      │      perfect_skull.json
        │  │      │      perfect_topaz.json
        │  │      │      
        │  │      ├─key  6BOSS钥匙光柱特效
        │  │      │      countess_key.json
        │  │      │      nihlathak_key.json
        │  │      │      summoner_key.json
        │  │      │      
        │  │      ├─quest  任务物品光柱特效
        │  │      │      bark_scroll.json
        │  │      │      book_of_skill.json
        │  │      │      burning_essence_of_terror.json
        │  │      │      charged_essense_of_hatred.json
        │  │      │      festering_essence_of_destruction.json
        │  │      │      gold_bird.json
        │  │      │      horadric_cube.json
        │  │      │      jade_figurine.json
        │  │      │      lam_esens_tome.json
        │  │      │      mephisto_soul_stone.json
        │  │      │      scroll_of_horadric_quest_info.json
        │  │      │      scroll_of_self_resurrect.json
        │  │      │      token_of_absolution.json
        │  │      │      twisted_essence_of_suffering.json
        │  │      │      
        │  │      ├─ring  戒指光柱特效
        │  │      │      ring.json
        │  │      │      
        │  │      └─rune  符文光柱的特效
        │  │              ber_rune.json
        │  │              cham_rune.json
        │  │              fal_rune.json
        │  │              gul_rune.json
        │  │              hel_rune.json
        │  │              io_rune.json
        │  │              ist_rune.json
        │  │              jah_rune.json
        │  │              ko_rune.json
        │  │              lem_rune.json
        │  │              lo_rune.json
        │  │              lum_rune.json
        │  │              mal_rune.json
        │  │              ohm_rune.json
        │  │              pul_rune.json
        │  │              sur_rune.json
        │  │              um_rune.json
        │  │              vex_rune.json
        │  │              zod_rune.json
        │  │              
        │  └─ui
        │      └─fonts
        │              blizzardglobal-v5_81.TTF  简体字体
        │              arfangxinshuh7c95b5_eb_t.ttf  繁体字体
        │              
        └─local
            └─lng
                ├─strings
                │      item-gems.json   宝石说明
                │      item-modifiers.json
                │      item-nameaffixes.json  前缀后缀定义，【超强的】以及【珠宝匠】等的定义
                │      item-names.json  物品名称定义，吐槽等内容
                │      item-runes.json  符文及符文之语定义
                │      levels.json  地图场景等级注释
                │      npcs.json
                │      quests.json  任务说明
                │      shrines.json
                │      ui.json  游戏界面，符文之语速查等
                │      vo.json
                │      
                └─subtitles
                    └─zhcn  矫正过场动画字幕
                            act02start.srt
                            act03start.srt
                            act04end.srt
                            act04start.srt
                            d2intro.srt
                            d2x_intro.srt
# A simple QQ Bot

## 这是什么
一个使用[graia-ariadne](https://github.com/GraiaProject/Ariadne)/[graia-saya](https://github.com/GraiaProject/Saya)写的bot  
如标题所言，相比于[SAGIRI-kawaii/sagiri-bot](https://github.com/SAGIRI-kawaii/sagiri-bot)这种大工程，本Bot仅仅是借助以上两个模块做了一点点的打包。假设未来有人想要通过这个文档学习saya也是一个不错的选择

## 前提提示
这个代码，我无法保证能够使用(因为这些代码是我写的代码的阉割版，并且每次push都不先test)
这个代码发布到github的最大意义，其实是让给那些正在写机器人的人一个参考

## 使用前的配置

```yaml
#config.yml
account: 10000 #你的QQ账号
verify_key: I_Love_Study #mirai-api-http config中的verify_key
miraiHost: http://localhost:8070 #mirai-api-http ws监视的端口
admin_group: 10086 #管理员所在的群(现暂时没有相关模块需要所以可以不用管)
ultra_administration: #最高权限人，可以控制模块的开启与关闭
  - 10001
load_modules_folder: #需要导入的文件夹
  - entertain
```

## 他能做什么
注：以下功能的所有用法都在每个模块的源文件中有写  
    部分模块可能没写(因为有点懒)
    []为必加参数，()为选加参数
现在他所能做的功能有：
  
### [DD直播间查看](entertain/dd)
功能介绍：通过调用指令判断现在那些人在直播，并且能够将直播间照片排列到一起发送  
调用指令："直播 [DD组织团体]" 和 "直播间 [DD组织团体]"  
需要第三方模块：aiohttp, pyyaml, pillow
  
### [小老弟表情包P图](entertain/pic)
功能介绍：返回一张"咋回事小老弟"的表情包并将发送者和被at者头像P到上面  
调用指令："小老弟" + 任意At (无先后顺序)  
需要第三方模块：pillow

### [petpet表情包P图](entertain/petpet)
功能介绍：返回一张petpet表情包并将被at者头像P到上面  
调用指令："摸头" + (任意At) (无先后顺序，如没有at则为发送者自己)  
~~抄袭~~借鉴： [SAGIRI-kawaii/sagiri-bot](https://github.com/SAGIRI-kawaii/sagiri-bot)  
需要第三方模块：pillow
  
### [番剧时刻表](entertain/anime_timesche.py )
功能介绍：发送B站昨天/今天/明天的番剧时刻表  
调用办法："anime ('tomorrow'/'yesterday')"  
需要第三方模块：aiohttp, pillow

### [禁言我](entertain/auto_ban.py)
功能介绍：在有管理员及以上权限的时候将发送"禁言我"的人随机时常禁言  
调用办法："经验我"  
需要第三方模块：无  

### [百科百科/热点](entertain/baidu.py)
功能介绍：获取相关词条的返回信息/获取百度热点Top10  
调用办法："百科 [词条] (序号)" | "热点"  
需要第三方模块：aiohttp, ujson, lxml  

### [番剧信息查看](entertain/bangumi.py)
功能介绍：获取番剧的详细信息  
调用办法："bangumi [番剧名称]"  
~~抄袭~~借鉴： [SAGIRI-kawaii/sagiri-bot](https://github.com/SAGIRI-kawaii/sagiri-bot)  
需要第三方模块：aiohttp

### [语音音乐条](entertain/bar_music.py)
功能介绍：以语音格式发送网易云音乐(注：只发前1min)  
调用办法："bar_music [音乐名称]"  
需要的第三方模块：graia-Template, graiax-silkcoder, [expand/Netease](expand/Netease.py)

### [今日二次元人物生日查看](entertain/birthday_searcher.py)
功能介绍：获取今天生日的虚拟人物  
调用办法："今天谁生日"  
需要的第三方模块：aiohttp, pillow, lxml

### [新冠累积查看](entertain/COVID.py)
功能介绍：获取新型冠状病毒类似感染Top20  
调用办法："COVID-19"  
需要的第三方模块: aiohttp, matplotlib, numpy

### [幻影坦克](entertain/ghost_tank.py)
功能介绍：制作幻影坦克  
调用办法："ghost_tank [图片1] [图片2]"  
需要的第三方模块：pillow, numpy

### [❤资源查看❤](entertain/material.py)
功能介绍：获取学习资料(指厚大法考)  
调用办法："learn"  
需要的第三方模块：无

### [萌娘百科信息](entertain/moegirl_info.py)
功能介绍：获取萌娘百科界面的卡片信息  
调用办法："萌娘百科 [词条]"  
需要的第三方模块：playwright

### [能不能好好说话](entertain/nbnhhsh.py)
功能介绍：获取缩写蕴含的意思  
调用办法："nbnhhsh [缩写]"  
需要的第三方模块：aiohttp

### [pornhub图标制作](entertain/ph.py)
功能介绍：制作类似pornhub图标的图标  
调用办法："ph [左文] [右文]"  
需要的第三方模块：pillow, [expand/text](expand/text.py)

### [B站视频/音频信息查看](entertain/bili)
功能介绍：获取B站视频(文字形式)/音频(图片形式)信息  
调用办法："[av号/BV号/AU号]"  
需要的第三方模块：pillow, [expand/bilibili](expand/bilibili.py)

## 未来要做的功能有：
 - ~~抄其他机器人的功能~~

## 如何开启/关闭群组
注：以下命令都需要在群里发送，并且用户in ultra_administration
```shell
setting group --add 114514 #添加群号为114514的管理(既启动该群模组)(无参数默认为发送该命令所在群)
setting group --delete 114514 #删除群号为114514的管理(且删除该群所有设置)(无参数默认为发送该命令所在群)

setting plugin -on entertain.baidu #启动百度模组
setting plugin -off entertain.baidu #关闭百度模组
setting plugin -on entertain #启动entertain文件夹下所有模组
setting plugin -off entertain #关闭entertain文件夹下所有模组

setting plugin -on entertain.baidu -g 114514 1919810 #支持自定义群(默认为命令发送所在群)
```
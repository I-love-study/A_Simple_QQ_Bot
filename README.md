# A simple QQ Bot

## 这是什么
一个使用graia-application-mirai写的垃圾代码(能用就行)

## 前提提示
这个代码，我无法保证能够使用(因为这些代码是我写的代码的阉割版，并且每次push都不先test)
这个代码发布到github的，其实是让给那些正在写机器人的人一个参考

## 他能做什么
注：以下功能的所有用法都在每个模块的'__plugin_usage__'变量
    部分模块可能没写(因为有点懒)
 
现在他所能做的功能有：
 - DD直播间查看(dd)
 - 小老弟表情包P图(pic)
 - 新番时刻表(anime_timesche)
 - 禁言我(auto_ban)
 - 百度百科，百度热点(baidu)
 - 番剧详细信息(bangumi)
 - 网易云音乐音频(bar_music)
 - 新冠疫情查询(COVID)
 - B张视频详细信息(video_info)
 - petpet图片制作(摸头@xxx)
 - pornhub图片制作(ph 左边文字 右边文字)
 - 涩图来(可自定义)

未来要做的功能有：
 - ~~抄其他机器人的功能~~
 - 更好的模块功能

## ~~抄了什么~~ 借鉴了什么
1.[ieew/miraibot](https://github.com/ieew/miraibot)的动态导入(用pathlib写了一遍)

2.[SAGIRI-kawaii/sagiri-bot](https://github.com/SAGIRI-kawaii/sagiri-bot)的get_bangumi_info/petpet/ph
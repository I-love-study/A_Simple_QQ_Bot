# A simple QQ Bot

## 这是什么
一个使用[graia-application-mirai](https://github.com/GraiaProject/Application)/[graia-saya](https://github.com/GraiaProject/Saya)写的bot  
如标题所言，相比于[SAGIRI-kawaii/sagiri-bot](https://github.com/SAGIRI-kawaii/sagiri-bot)这种大工程，本Bot仅仅是借助以上两个模块做了一点点的打包

## 前提提示
这个代码，我无法保证能够使用(因为这些代码是我写的代码的阉割版，并且每次push都不先test)
这个代码发布到github的最大意义，其实是让给那些正在写机器人的人一个参考

## 使用前的配置

```yaml
#config.yml
account: 10000 #你的QQ账号
authKey: I_Love_Study #mirai-api-http config中的authKey
miraiHost: http://localhost:8070 #mirai-api-http ws监视的端口
admin_group: 10086 #管理员所在的群(现暂时没有相关模块需要所以可以不用管)
ultra_administration: #最高权限人，可以控制模块的开启与关闭
  - 1450069615
load_modules_folder: #需要导入的文件夹
  - entertain
```

## 他能做什么
注：以下功能的所有用法都在每个模块的源文件中有写  
    部分模块可能没写(因为有点懒)
现在他所能做的功能有：
|功能|文件名|~~抄袭~~借鉴|备注|
|:--:|:--:|:--:|:--:|
|DD直播间查看|dd||需要重写dd_info.yml(源数据已经过时)
|小老弟表情包P图|pic||
|新番时刻表|anime_timesche||
|禁言我|auto_ban||需要账号为管理员极以上
|百度百科，百度热点|baidu|
|番剧详细信息|bangumi|[SAGIRI-kawaii/sagiri-bot](https://github.com/SAGIRI-kawaii/sagiri-bot)|
|网易云音乐音频|bar_music||发出的音乐只有前1min
|新冠疫情查询|COVID||
|B站视频详细信息|video_info|
|petpet图片制作|petpet|[SAGIRI-kawaii/sagiri-bot](https://github.com/SAGIRI-kawaii/sagiri-bot)|
|pornhub图片制作|ph|支持emoji但是不支持QQ自带表情
|涩图来|ero||需要自定义

未来要做的功能有：
 - ~~抄其他机器人的功能~~

## 如何开启/关闭群组
注：以下命令都需要在群里发送，并且用户为ultra_administration
```shell
setting group --add 114514 #添加群号为114514的管理(既启动该群模组)
setting group --delete 114514 #删除群号为114514的管理(且删除该群所有设置)

setting plugin -on entertain.baidu #启动百度模组
setting plugin -off entertain.baidu #关闭百度模组
setting plugin -on entertain #启动entertain文件夹下所有模组
setting plugin -off entertain #关闭entertain文件夹下所有模组

setting plugin -on entertain.baidu -g 114514 1919810 #支持自定义群(默认为命令发送所在群)
```
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import *
from graia.ariadne.model import Group, Member
from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.scheduler.saya.schema import SchedulerSchema
from graia.scheduler import timers

import asyncio
import sqlite3
import datetime
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.gridspec import GridSpec
from io import BytesIO
from pathlib import Path

mpl.use('Agg')

def get_month(d=datetime.date.today()):
    return f"{d.year}-{str(d.month).zfill(2)}"

p = Path('data/chat_log')
if not p.exists(): p.mkdir(parents=True, exist_ok=True)

log_name = get_month()
#log_name = "2021-10"
conn = sqlite3.connect(f'data/chat_log/{log_name}.db', isolation_level = None)
cur = conn.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS log (
    SENDTIME  DATETIME     NOT NULL,
    GROUPID    INTEGER     NOT NULL,
    MEMBERID   INTEGER     NOT NULL,
    MESSAGE       TEXT     NOT NULL
    );''')

saya = Saya.current()
channel = Channel.current()
admin_group = saya.access('all_setting')['admin_group']

@channel.use(SchedulerSchema(timers.crontabify('0 0 * * *')))
async def update_log(app: Ariadne):
    global log_name, conn, cur
    await asyncio.sleep(3)
    d = get_month()
    if d != log_name:
        log_name = d
        conn_, cur_ = conn, cur
        conn = sqlite3.connect(f'data/chat_log/{log_name}.db', isolation_level = None)
        cur = conn.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS log (
            SENDTIME  DATETIME     NOT NULL,
            GROUPID    INTEGER     NOT NULL,
            MEMBERID   INTEGER     NOT NULL,
            MESSAGE       TEXT     NOT NULL
            );''')
    
        sql_cmd = "SELECT * from log where SENDTIME >= datetime('Now', 'localtime', 'start of day')"
        cur.executemany("INSERT into log values (?, ?, ?, ?)", cur_.execute(sql_cmd))
        cur_.execute("DELETE from log where SENDTIME >= datetime('Now', 'localtime', 'start of day')")
        cur_.close()
        conn_.close()


@channel.use(SchedulerSchema(timers.crontabify('1 0 * * *')))
async def send_log(app: Ariadne):
    send_date = datetime.date.today()-datetime.timedelta(days = 1)
    #send_date=datetime.date.today().isoformat()
    conn_ = sqlite3.connect(f'data/chat_log/{get_month(send_date)}.db')
    cur_ = conn_.cursor()

    font = fm.FontProperties(fname='src/font/SourceHanSans-Medium.otf')
    #plt.figure(figsize=(10,5), dpi=100)
    mpl.rc_file_defaults()
    plt.style.use("dark_background")
    fig = plt.figure(figsize=(10, 10), constrained_layout=True)
    gs = GridSpec(2, 1, height_ratios=[8,3], figure=fig)
    ax1, ax2 = plt.subplot(gs[0]), plt.subplot(gs[1])

    sql_cmd = (
        "SELECT COUNT(SENDTIME) from log where "
        "SENDTIME >= datetime('Now', 'localtime', 'start of day', '-{} hours') and "
        "SENDTIME < datetime('Now', 'localtime', 'start of day', '-{} hours')")
    data = [list(cur_.execute(sql_cmd.format(t+1, t)))[0][0] for t in reversed(range(24))]
    ax1.set_xlabel('时间(h)', fontproperties=font)
    ax1.set_ylabel('接收群数据', fontproperties=font)
    ax1.set_title(f'今日机器人数据查看\n累计接收信息{sum(data)}条', fontproperties=font)
    ax1.plot(list(range(24)), data, color = "#0C88DA", 
        marker='o', markerfacecolor = '#787878',markersize = 5)
    for a, b in zip(list(range(24)), data):
        ax1.text(a, b, b, ha='center', va='bottom', fontsize=10, fontproperties=font)
    
    sql_cmd = (
        "SELECT COUNT(SENDTIME) from log where "
        "SENDTIME >= datetime('Now', 'localtime', 'start of day', '-1 day') and "
        "SENDTIME < datetime('Now', 'localtime', 'start of day') and GROUPID == {}")
    g = {"#1": 991545779, "#2": 796156151, "#3": 568017603, "#4": 753510813}
    data = [list(cur_.execute(sql_cmd.format(sg)))[0][0] for sg in reversed(g.values())]
    ax2.set_ylabel('群名', fontproperties=font)
    ax2.set_xlabel('接收群数据', fontproperties=font)
    ax2.set_title(f'今日各群消息发送数量查看', fontproperties=font)
    c = ax2.barh(range(len(g)), data, color="#0C88DA")
    ax2.bar_label(c, data)
    ax2.set_yticks(range(len(g)))
    ax2.set_yticklabels(reversed(g.keys()))

    read = BytesIO()
    plt.savefig(read, format = "png", bbox_inches='tight')
    plt.clf()
    await app.sendGroupMessage(admin_group, MessageChain.create([
        Plain('今日机器人接收信息：'),
        Image(data_bytes=read.getvalue()),
        ]))
    cur_.close()
    conn_.close()

@channel.use(ListenerSchema(listening_events=[GroupMessage]))
async def log(app: Ariadne, group: Group, message: MessageChain, member:Member):
    data = [datetime.datetime.now(), group.id, member.id, message.asPersistentString(binary=False)]
    cur.execute("INSERT into log values (?, ?, ?, ?)", data)

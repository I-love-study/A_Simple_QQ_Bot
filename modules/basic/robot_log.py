import asyncio
import datetime
import sqlite3
from io import BytesIO
from pathlib import Path

import matplotlib
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain, Image
from graia.ariadne.model import Group, Member
from graia.saya import Channel, Saya
from graiax.shortcut.saya import listen, crontab

matplotlib.use('Agg')

def get_month(d=datetime.date.today()):
    return f"{d.year}-{str(d.month).zfill(2)}"

p = Path('data/chat_log')
if not p.exists(): p.mkdir(parents=True, exist_ok=True)

log_name = get_month()
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
lock = asyncio.Lock()

@crontab('0 0 * * *')
async def update_log(app: Ariadne):
    global log_name, conn, cur
    await asyncio.sleep(3)
    
    if (d := get_month()) == log_name:
        return
    
    async with lock:
        sql_cmd = "SELECT * from log where SENDTIME >= datetime('Now', 'localtime', 'start of day')"
        cur.executemany("INSERT into log values (?, ?, ?, ?)", cur.execute(sql_cmd))
        cur.execute("DELETE from log where SENDTIME >= datetime('Now', 'localtime', 'start of day')")
        cur.close()
        conn.close()

        log_name = d
        conn = sqlite3.connect(f'data/chat_log/{log_name}.db', isolation_level = None)
        cur = conn.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS log (
            SENDTIME  DATETIME     NOT NULL,
            GROUPID    INTEGER     NOT NULL,
            MEMBERID   INTEGER     NOT NULL,
            MESSAGE       TEXT     NOT NULL
            );''')

@listen(GroupMessage)
async def log(app: Ariadne, group: Group, message: MessageChain, member:Member):
    data = [datetime.datetime.now(), group.id, member.id, message.as_persistent_string(binary=False)]
    cur.execute("INSERT into log values (?, ?, ?, ?)", data)


@crontab('1 0 * * *')
async def send_log(app: Ariadne):
    await asyncio.sleep(5)
    send_date = datetime.date.today()-datetime.timedelta(days = 1)
    #send_date=datetime.date.today().isoformat()
    conn_ = sqlite3.connect(f'data/chat_log/{get_month(send_date)}.db')
    cur_ = conn_.cursor()
    sql_cmd = (
        "SELECT COUNT(SENDTIME) from log where "
        "SENDTIME >= datetime('Now', 'localtime', 'start of day', '-{} hours') and "
        "SENDTIME < datetime('Now', 'localtime', 'start of day', '-{} hours')")
    data = [list(cur_.execute(sql_cmd.format(t+1, t)))[0][0] for t in reversed(range(24))]

    font = fm.FontProperties(fname='static/font/SourceHanSans-Medium.otf') # type: ignore
    plt.figure(figsize=(10,5), dpi=100)
    plt.style.use("dark_background")
    plt.xlabel('时间(h)', fontproperties=font)
    plt.ylabel('接收群数据', fontproperties=font)
    plt.title(f'今日机器人数据查看\n累计接收信息{sum(data)}条', fontproperties=font)
    plt.plot(list(range(24)), data, color = "#0C88DA", 
        marker='o', markerfacecolor = '#787878',markersize = 5)
    for a, b in zip(list(range(24)), data):
        plt.text(a, b, b, ha='center', va='bottom', fontsize=10, fontproperties=font)
    #plt.show()
    read = BytesIO()
    plt.savefig(read, format = "png", bbox_inches='tight')
    plt.clf()
    await app.send_group_message(admin_group, MessageChain([
        Plain('今日机器人接收信息：'),
        Image(data_bytes=read.getvalue()),
        ]))
    cur_.close()
    conn_.close()
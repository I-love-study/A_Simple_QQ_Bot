import aiofiles

with open('data/黑名单.txt','r',encoding = 'UTF-8') as f:
    listing = [int(a.replace('\n','')) for a in f.readlines()]

async def update():
    global listing
    async with aiofiles.open('data/黑名单.txt', 'w', encoding = 'UTF-8') as f:
        await f.write("\n".join(str(q_id) for q_id in listing))
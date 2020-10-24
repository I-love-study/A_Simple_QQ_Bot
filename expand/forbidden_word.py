import csv

with open('data/违禁词.csv','r',encoding = 'UTF-8') as f:
    print('login')
    forbidden_data = []
    for a in csv.DictReader(f):
        a.update({'mute':int(a['mute']), 'OCR':bool(int(a['OCR']))})
        forbidden_data.append(a)

async def check(data: str):#违禁词判断
    ret = []
    for forbidden_word in forbidden_data:
        if all([word.upper() in data.upper() for word in forbidden_word['word'].split('|')]):
            ret.append(forbidden_word)
    return ret
import yaml
import requests
live_api = "http://api.live.bilibili.com/bili/living_v2/"

hololive_ids=[511613157, 511613155, 511613156, 491474050,
              491474049, 491474051, 491474048, 491474052,
              456368455, 444316844, 354411419, 427061218,
              454955503, 455172819, 454733056, 454737600,
              9034870, 443305053, 443300418, 389056211,
              412135619, 412135222, 366690056, 286179206,
              389856447, 339567211, 389862071, 389858027,
              332704117, 336731767, 389857131, 389857640,
              20813493, 389859190, 389858754, 375504219]

Hanayori_ids=[316381099,441403698,441381282,441382432]

paryi_hop_ids=[1576121,198297,18149131,372984197,
               349991143,8119834,2778044,3149619,
               2191383,6055289,380829248,1869304,
               1429475,406805563,2299184,435569969,
               407106379,401480763,442902274,10077023,
               452100632,386900246,98181,480432362,
               511613155,11073,282994]

final_data = {}

room_data = []
for a in hololive_ids:
	room_id = requests.get(live_api + str(a)).json()['data']['url'].split(r'/')[-1]
	room_data.append(int(room_id))
final_data['Hololive'] = {'mid':hololive_ids, 'room_id':room_data}

room_data = []
for a in Hanayori_ids:
	room_id = requests.get(live_api + str(a)).json()['data']['url'].split(r'/')[-1]
	room_data.append(int(room_id))
final_data['Hanayori'] = {'mid':Hanayori_ids, 'room_id':room_data}

room_data = []
for a in paryi_hop_ids:
	room_id = requests.get(live_api + str(a)).json()['data']['url'].split(r'/')[-1]
	if room_id:
		room_data.append(int(room_id))
	else:
		paryi_hop_ids.remove(a)
final_data['Paryi_hop'] = {'mid':paryi_hop_ids, 'room_id':room_data}


with open('message.yml', 'w', encoding = 'UTF-8') as f:
    yaml.dump(final_data,f)

import json

def get_info():
    with open('Data/players_info.json','r') as dat:
        info = json.load(dat)
    return info

def get_wins_losses(info,player):
    return info[player]['sets']['h2hs']


info = get_info()

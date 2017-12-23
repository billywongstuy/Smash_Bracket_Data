import json

with open('Data/players_info.json','r') as dat:
    p_info = json.load(dat)
with open('Data/lower_tags.json','r') as dat:
    l_tags = json.load(dat)
    
group = ['Abadango','Ally','CaptainZack','Dabuz','Fatality','KEN','Kirihara','komorikiri','Larry Lurr','MKLeo','Nairo','Salem','Samsora','Shuton','T','Tweek','VoiD','WaDi','ZeRo']

#group = ['Dabuz','KEN','Samsora','T']
#group = ['Abadango','CaptainZack','komorikiri','Nairo']
#group = ['Ally','Tweek','VoiD','WaDi']
#group = ['Kirihara','MKLeo','Salem','Shuton']
#group = ['Fatality','Larry Lurr','ZeRo']

group = [l_tags[p.lower()] for p in group]

players = {}

for player in group:
    players[player] = {'sets':{'wins':{},'losses':{}},'total':0,'wins':0,'losses':0}
    
    sets = p_info[player]['sets']
    for opp in sets['wins']:
        if opp in group:
            players[player]['sets']['wins'][opp] = sets['wins'][opp]
            players[player]['total'] += sets['wins'][opp]['amount']
            players[player]['wins'] += sets['wins'][opp]['amount']
    for opp in sets['losses']:
        if opp in group:
            players[player]['sets']['losses'][opp] = sets['losses'][opp]
            players[player]['total'] += sets['losses'][opp]['amount']
            players[player]['losses'] += sets['losses'][opp]['amount']

win_percents = {}
for p in players:
    if players[p]['total'] != 0:
        win_percents[p] = players[p]['wins']*100.0/players[p]['total']
    else:
        win_percents[p] = -1
        
win_percents = sorted([(p,win_percents[p]) for p in win_percents], key=lambda x:-x[1])

for p in win_percents:
    print p[0],p[1]

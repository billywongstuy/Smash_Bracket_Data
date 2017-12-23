import csv, json, os, math
from fractions import Fraction

ignore_place = ['PAX Arena at PAX West 2017']

#adjust so that Ryuga falls into top 50 and 9B drops out?

'''
OFF
"Ranai": 17,
"9B": 23,
"6WX": 31,
"T": 32,
"Earth": 35,
"HIKARU": 36,
"Ned": 37,
"Rich Brown": 38,
"Myran": 39,
"ScAtt": 41,
"Nietono": 43,
"Ac": 45,
"Edge": 47,
"FOW": 50
'''

min_tournaments = 2
max_full_tournaments = 4
wins_percent = .60
placements_percent = .40

def atoi(string):
    int_string = ''
    for c in string:
        if c.isdigit():
            int_string += c
    return int(int_string)

def curve_score(score):
    return round(math.sqrt(score)*10,2)

def double_curve_score(score):
    return round(math.sqrt(math.sqrt(score)*10)*10,2)


f = open('Data/point_awards.txt','r')
dat = f.read().split('\n')[:-1]
pt_awards = {}
for row in dat:
    parts = row.split(':')
    pt_awards[parts[0]] = Fraction(parts[1])
f.close()
pt_awards['10th'] = pt_awards['9th']
pt_awards['11th'] = pt_awards['13th']
pt_awards['16th'] = pt_awards['13th']

def places_order():
    places = open('Output/placements.csv','r')
    info = csv.DictReader(places)

    f = open('Data/tts_values.csv','r')
    dat = f.read().split('\n')[:-1]
    t_vals = {}
    for row in dat:
        parts = row.split(',')
        t_vals[parts[0]] = int(parts[1])
    f.close()

    players_pts = {}
    
    for player in info:
        #print player
        pts = []
        tag = str(player[''])
        
        for key in player:
            
            if key not in ignore_place and key != '' and player[key] != '':
                pts.append(float(pt_awards[player[key]]*t_vals[key]))
            
            #key is the tournament

            #if key != '' and player[key] != '':
            #    pts.append(1.0/math.sqrt(atoi(player[key]))*t_vals[key])
            
            

        if len(pts) >= min_tournaments:
            if tag not in players_pts:
                players_pts[tag] = 0
            
            for i in xrange(max_full_tournaments):
                if i < len(pts):
                    big = max(pts)
                    pts.remove(big)
                    players_pts[tag] += big

            #players_pts[tag] += sum(pts)*.75
            players_pts[tag] += sum(pts)*.75
   
        
    places.close()
    players_pts = [(key,players_pts[key]) for key in players_pts]
    players_pts.sort(key=lambda x:-x[1])

    big_pts = players_pts[0][1]
    
    a = open('Output/rank_place.txt','w')
    i = 0
    while i < len(players_pts):
        rank = '%d,%s,%f\n' % (i+1,players_pts[i][0],players_pts[i][1]*100/big_pts)
        a.write(rank)
        i += 1
    a.close()


def apply_wins_to_places():

    # the win points should scale more drastically
    
    w_vals = {}
    rank_extra = 0
    val_start = 1000

    while val_start > 0 and rank_extra <= 100:
        for x in xrange(rank_extra+1,rank_extra+11):
            w_vals[x] = val_start
        #print val_start
        rank_extra += 10
        val_start -= (7+rank_extra*(40.0/10))    
        
        
        
    f = open('Output/rank_place.txt','r')
    data = f.read().split('\n')[:-1]
    ranked = {}
    for row in data:
        parts = row.split(',')
        ranked[parts[1]] = (int(parts[0]),float(parts[2]))
    f.close() 
    
    w_pts = {}
    f = open('Output/h2hs.csv','r')
    players = csv.DictReader(f)
    for player in players:
        tag = str(player[''])
        if tag in ranked:
            if tag not in w_pts:
                w_pts[tag] = 0
            for opp in player:
                if opp != '' and player[opp] != '':
                    if opp in ranked and ranked[opp][0] in w_vals and ranked[opp][0] <= 100:
                        #pts_given = w_vals[ranked[opp][0]]
                        #pts_given = 100*(101-ranked[key][0])
                        pts_given = 100*(101-ranked[opp][0])
                        
                        h2h = player[opp].split('-')
                        
                        w_pts[tag] += int(h2h[0])*pts_given
    f.close()

    
    players = [p for p in w_pts]
    
    max_p_pts = ranked[max(ranked,key=lambda x:ranked[x][1])][1]
    max_w_pts = w_pts[max(w_pts,key=lambda x:w_pts[x])]
    
    
    total_pts = {p:0 for p in w_pts}
    for p in players:
        total_pts[p] = curve_score(wins_percent*w_pts[p]*100/max_w_pts + placements_percent*(ranked[p][1]*100/max_p_pts))
        #total_pts[p] = curve_score((w_pts[p]*100/max_w_pts + ranked[p][1]*100/max_p_pts)/2)
        
    total_pts = [(key,total_pts[key]) for key in total_pts]
    total_pts.sort(key=lambda x:-x[1])
    
    a = open('Output/rank_both.txt','w')
    i = 0
    while i < len(total_pts):
        rank = '%d,%s,%f\n' % (i+1,total_pts[i][0],total_pts[i][1])
        a.write(rank)
        i += 1
    a.close()


    w_pts = [(key,w_pts[key]) for key in w_pts]
    w_pts.sort(key=lambda x:-x[1])
    a = open('Output/rank_wins.txt','w')
    i = 0
    while i < len(w_pts):
        rank = '%d,%s,%f\n' % (i+1,w_pts[i][0],w_pts[i][1])
        a.write(rank)
        i += 1
    a.close()

    
    
def ranked_stats():

    with open('Data/players_info.json','r') as dat:
        info = json.load(dat)
    
    f = open('Output/rank_both.txt','r')
    players = f.read().split('\n')[:-1]
    f.close()
    
    f = open('Data/tts_values.csv','r')
    dat = f.read().split('\n')[:-1]
    t_vals = {}
    for row in dat:
        parts = row.split(',')
        t_vals[parts[0]] = int(parts[1])
    f.close()

    ranked = {}
    players = players[:min(100,len(players))]
    for p in players:
        parts = p.split(',')
        if parts[1] not in ranked:
            ranked[parts[1]] = info[parts[1]]
            ranked[parts[1]]['rank'] = int(parts[0])
            ranked[parts[1]]['score'] = float(parts[2])

    for p in ranked:
        ranked[p]['t10'] = {'W':0,'L':0}
        ranked[p]['t50'] = {'W':0,'L':0}
        ranked[p]['wins_50'] = []
        ranked[p]['losses_50'] = []
        ranked[p]['losses_other'] = []
        
        for opp in ranked[p]['sets']['wins']:
            if str(opp) in ranked and ranked[str(opp)]['rank'] <= 50:
                if ranked[str(opp)]['rank'] <= 10:
                    ranked[p]['t10']['W'] += ranked[p]['sets']['wins'][opp]['amount']
                ranked[p]['t50']['W'] += ranked[p]['sets']['wins'][opp]['amount']
                ranked[p]['wins_50'].append((str(opp),[str(t) for t in ranked[p]['sets']['wins'][opp]['when']]))

        for opp in ranked[p]['sets']['losses']:
            if str(opp) in ranked and ranked[str(opp)]['rank'] <= 50:
                if ranked[str(opp)]['rank'] <= 10:
                    ranked[p]['t10']['L'] += ranked[p]['sets']['losses'][opp]['amount']
                ranked[p]['t50']['L'] += ranked[p]['sets']['losses'][opp]['amount']
                ranked[p]['losses_50'].append((str(opp),[str(t) for t in ranked[p]['sets']['losses'][opp]['when']]))
            else:
                ranked[p]['losses_other'].append((str(opp),[str(t) for t in ranked[p]['sets']['losses'][opp]['when']]))

        ranked[p]['wins_50'].sort(key=lambda x:ranked[x[0]]['rank'])
        ranked[p]['losses_50'].sort(key=lambda x:ranked[x[0]]['rank'])

        
    os.system('rm Output/Player_Stats/*')
    for p in ranked:
        f = open('Output/Player_Stats/%s_%d.txt' % (p.replace('/','-'),ranked[p]['rank']),'w')
        form = '''Player: %s
Rank: %d
Points: %f

Top 10 Record: %d-%d
Top 50 Record: %d-%d

Tournaments:
''' % (p,ranked[p]['rank'],ranked[p]['score'],ranked[p]['t10']['W'],ranked[p]['t10']['L'],ranked[p]['t50']['W'],ranked[p]['t50']['L'])
        f.write(form)

        placings = []
        for t in ranked[p]['placings']:
            if t not in ignore_place:
                value = pt_awards[ranked[p]['placings'][t]]*t_vals[t]
                placings.append((t,ranked[p]['placings'][t],value))
        placings.sort(key=lambda x:-x[2])
        for t in placings:
            f.write('%s: %s\n' % (t[0],t[1]))

        f.write('\nWins Top 50:\n')
        for w in ranked[p]['wins_50']:
            f.write('%s\n' % (str(w)))
        f.write('\nLosses Top 50:\n')
        for l in ranked[p]['losses_50']:
            f.write('%s\n' % (str(l)))
        f.write('\nLosses Other:\n')
        for l in ranked[p]['losses_other']:
            f.write('%s\n' % (str(l)))

            
        f.close()
        
    
places_order()
apply_wins_to_places()
ranked_stats()

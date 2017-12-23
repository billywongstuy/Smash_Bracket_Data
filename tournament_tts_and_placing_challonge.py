import json
import challonge_api

tiers = {3600: 'S+', 2400: 'S', 1200: 'A', 600: 'B', 300: 'C'}
pgr_cutoffs = {'S+': 64, 'S': 64, 'A': 32, 'B': 16, 'C': 8}

def num_suffix(n):
    if n >= 10 and n <= 20:
        return '%dth' % (n)
    elif n%10 == 1:
        return '%dst' % (n)
    elif n%10 == 2:
        return '%dnd' % (n)
    elif n%10 == 3:
        return '%drd' % (n)
    else:
        return '%dth' % (n)

def omit_character(tag):
    index = tag.find(' (')
    return tag[:index]

def omit_sponsor(tag):
    start = 0 if tag.rfind('| ') == -1 else tag.rfind('| ')+2
    return tag[start:].encode('ascii','replace')


def get_placements(link,cutoff):
    players = challonge_api.get(link,'participants')

    placement_indices = {1:1, 2:2, 3:3, 4:4, 5:5, 7:7, 9:9, 13:13, 17:17, 25:25, 33:33, 49:49}
    placements = [None] * (cutoff+1)
    
    for p in players:
        p_name = omit_sponsor(omit_character(p['participant']['name']))
        placement = p['participant']['final_rank']
        if type(placement) == int and placement <= cutoff:
            if placement not in placement_indices:
                placement_indices[placement] = placement
            placements[placement_indices[placement]] = [p_name, num_suffix(placement)]
            placement_indices[placement] += 1

    return placements


def get_placements_and_pgr_tts(link,entrants,pot=0):
    
    players = challonge_api.get(link,'participants')
    
    with open('Data/PGR_Players.json') as dat:
        pgr_players = json.load(dat)['players']
    pgr_players['Tsu-'] = 26
    pgr_players['Komorikiri'] = 8
    
    info = {}
    PGR_1_5 = []
    PGR_6_10 = []
    PGR_11_20 = []
    PGR_21_30 = []
    PGR_31_50 = []
    placement_indices = {1:1, 2:2, 3:3, 4:4, 5:5, 7:7, 9:9, 13:13, 17:17, 25:25, 33:33, 49:49}
    placements = [None] * 65
    
    for p in players:

        p_name = omit_sponsor(omit_character(p['participant']['name']))
        placement = p['participant']['final_rank']
        
        if p_name in pgr_players:
            if pgr_players[p_name] <= 5:
                PGR_1_5.append('%d: %s' % (pgr_players[p_name], p_name))
            elif pgr_players[p_name] <= 10:
                PGR_6_10.append('%d: %s' % (pgr_players[p_name], p_name))
            elif pgr_players[p_name] <= 20:
                PGR_11_20.append('%d: %s' % (pgr_players[p_name], p_name))
            elif pgr_players[p_name] <= 30:
                PGR_21_30.append('%d: %s' % (pgr_players[p_name], p_name))
            else:
                PGR_31_50.append('%d: %s' % (pgr_players[p_name], p_name))
                
        if type(placement) == int and placement <= 49:
            if placement not in placement_indices:
                placement_indices[placement] = placement
            placements[placement_indices[placement]] = [p_name, num_suffix(placement)]
            placement_indices[placement] += 1

    info['entrants'] = [entrants, entrants*2]
    info['PGR_1_5'] = [len(PGR_1_5), len(PGR_1_5)*224]
    info['PGR_6_10'] = [len(PGR_6_10), len(PGR_6_10)*128]
    info['PGR_11_20'] = [len(PGR_11_20), len(PGR_11_20)*96]
    info['PGR_21_30'] = [len(PGR_21_30), len(PGR_21_30)*80]
    info['PGR_31_50'] = [len(PGR_31_50), len(PGR_31_50)*64]
    info['pot'] = [pot,int(pot*0.04)]

    entrant_value = info['entrants'][1] + info['pot'][1]
    PGR_value = info['PGR_1_5'][1] + info['PGR_6_10'][1] + info['PGR_11_20'][1] + info['PGR_21_30'][1] + info['PGR_31_50'][1] 

    value = max(entrant_value, PGR_value)
    tier = 'S+' if value >= 3600 else 'S' if value >= 2400 else 'A' if value >= 1200 else 'B' if value >= 600 else 'C' if value >= 300 else '-'

    info['tier'] = tier
    info['value'] = value
    info['placements'] = placements
    info['pgr_cutoff'] = pgr_cutoffs[tier]
    
    return info


#print get_placements_and_pgr_tts('http://challonge.com/Umebura27T',224)['placements']
    

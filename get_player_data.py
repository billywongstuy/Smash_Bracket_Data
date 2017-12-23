import json, os
from collections import OrderedDict
import tournament_sets_smashgg as sets_smashgg
import tournament_tts_and_placing_smashgg as placing_smashgg
import tournament_sets_challonge as sets_challonge
import tournament_tts_and_placing_challonge as placing_challonge

'''
Figure out what to do with upper and lower case

'''

#better off to have an identifer

#exception for 2gg
#change in rankings too for 9th and below
gg_p = [['Ally','9th'],['Nairo','10th'],['Samsora','11th'],['CaptainZack','11th'],['WaDi','11th'],['Kirihara','11th'],['Larry Lurr','11th'],['komorikiri','16th'],['T','16th'],['Tweek','16th'],['Shuton','16th'],['Fatality','16th']]


def get_results():

    ordered_placements = []
    tournament_values = OrderedDict()
    
    with open('Data/Tournaments.json','r') as dt:
        tournaments = json.load(dt, object_pairs_hook=OrderedDict)
        
    try:
        with open('Data/parsed_tournaments.json') as dat:
            parsed = json.load(dat)
    except:
        parsed = {}

    for tourney in tournaments:
        #print tourney
        if tourney in parsed:
            pass
        else:
            if tournaments[tourney][1] == 'smash.gg':
                info = placing_smashgg.get_placements_and_pgr_tts(tournaments[tourney][0])
            else:
                entrants = int(raw_input('Enter number of entrants for %s: ' % (tourney))) 
                info = placing_challonge.get_placements_and_pgr_tts(tournaments[tourney][0],entrants)
            placements = info['placements'][0:info['pgr_cutoff']+1]
            placements[0] = tournaments[tourney]
            if tourney == '2GG Championship':
                placements[10:] = gg_p
            ordered_placements.append((tourney,placements))
            tournament_values[tourney] = info['value']
            
    all_results = OrderedDict(ordered_placements)

    f = open('Data/tts_values.csv','a')
    for key in tournament_values:
        f.write('%s,%d\n' % (key,tournament_values[key]))
    f.close()
    
    return all_results


#ignore_placings = ['PAX Arena at PAX West 2017']
ignore_placings = []
ignore_sets = []

def parse_results_and_sets():

    results = get_results()
    print 'Results received'

    try:
        with open('Data/lower_tags.json') as dat:
            lower_tags = json.load(dat)
    except:
        lower_tags = {}
    
    try:
        with open('Data/players_info.json') as dat:
            players_all = json.load(dat)
    except: 
        players_all = {}
    
    try:
        with open('Data/parsed_tournaments.json') as dat:
            names = json.load(dat, object_pairs_hook=OrderedDict)
    except:
        names = {}

    qualif_players = []
    for t in results:
        placers = results[t][1:]
        #print placers
        #print t

        for p in placers:
            low_tag = p[0].lower()
            if low_tag not in lower_tags:
                lower_tags[low_tag] = [p[0]]
            elif p[0] not in lower_tags[low_tag]:
                lower_tags[low_tag].append(p[0])
            if p[0] not in qualif_players:
                qualif_players.append(p[0]) 
    
    #for p in qualif_players:
    
    for p in lower_tags:
        #print type(lower_tags[p]), lower_tags[p]
        tags_string = ''.join(t+'/' for t in lower_tags[p])[:-1] if type(lower_tags[p]) == list else lower_tags[p]
        
        if tags_string not in players_all:
            #players_all[str(p)] = {'sets': {'wins': {}, 'losses': {}, 'h2hs': {}}, 'placings': OrderedDict()}
            
            lower_tags[p] = tags_string
            #print tags_string
            players_all[lower_tags[p]] = {'sets': {'wins': {}, 'losses': {}, 'h2hs': {}}, 'placings': OrderedDict()}
                        
    for tournament in results:
        link = results[tournament][0][0]
        mode = results[tournament][0][1]
        placings = results[tournament][1:]
        for player in placings:
            if player != None:
                if str(tournament) not in ignore_placings:
                    #players_all[str(player[0])]['placings'][str(tournament)] = player[1]
                    players_all[lower_tags[player[0].lower()]]['placings'][str(tournament)] = player[1]
                    
        print 'Done with placements for %s. Now looking at sets.' % (tournament)
        
        if mode == 'smash.gg':
            players_sets = sets_smashgg.get_mult_players_sets(link,qualif_players)
        else:
            players_sets = sets_challonge.get_mult_players_sets(link,qualif_players)

            
        for _player in players_sets:
            '''
            path = players_sets[str(_player)]['path']
            p_wins = players_all[str(_player)]['sets']['wins']
            p_losses = players_all[str(_player)]['sets']['losses']
            '''
            
            path = players_sets[str(_player)]['path']
            p_wins = players_all[lower_tags[_player.lower()]]['sets']['wins']
            p_losses = players_all[lower_tags[_player.lower()]]['sets']['losses']
            
            
            for opp in path:
                if opp[1] == 'W':
                    set_dest = p_wins
                    h2h_dest = 0
                else:
                    set_dest = p_losses
                    h2h_dest = 1

                
                '''
                if str(opp[0]) not in set_dest:
                    set_dest[opp[0]] = {'amount':0, 'when':[]}
               
                set_dest[opp[0]]['amount'] += 1
                set_dest[opp[0]]['when'].append(str(tournament))

                if opp[0] not in players_all[_player]['sets']['h2hs']:
                    players_all[_player]['sets']['h2hs'][opp[0]] = [0,0]
                players_all[_player]['sets']['h2hs'][opp[0]][h2h_dest] += 1
                '''

                #print qualif_players
                opp_lower = lower_tags[opp[0].lower()] if opp[0] in qualif_players else opp[0]
                
                if opp_lower not in set_dest:
                    set_dest[opp_lower] = {'amount':0, 'when':[]}
               
                set_dest[opp_lower]['amount'] += 1
                set_dest[opp_lower]['when'].append(str(tournament))

                low_player = lower_tags[_player.lower()]
                if opp_lower not in players_all[low_player]['sets']['h2hs']:
                    players_all[low_player]['sets']['h2hs'][opp_lower] = [0,0]
                players_all[low_player]['sets']['h2hs'][opp_lower][h2h_dest] += 1
                
        print 'Done with sets'
        names[str(tournament)] = ''
        
    players_all = OrderedDict(sorted(players_all.items()))

    with open('Data/parsed_tournaments.json','w') as dat:
        json.dump(names, dat)
    with open('Data/lower_tags.json','w') as dat:
        json.dump(lower_tags, dat)
        
    return players_all


def parsed_tournaments():
    with open('Tournaments.json','r') as dat:
        tours = json.load(dat)

        names = []

        for t in tours:
            names.append(str(t))
    return names




o = parse_results_and_sets()

p = json.dumps(o)
f = open('Data/players_info.json','w')
f.write(p)
f.close()




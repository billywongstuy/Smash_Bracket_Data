import json, os
from collections import OrderedDict

import tournament_sets_smashgg as sets_smashgg
import tournament_tts_and_placing_smashgg as placing_smashgg
import tournament_sets_challonge as sets_challonge
import tournament_tts_and_placing_challonge as placing_challonge

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
            ordered_placements.append((tourney,placements))
            tournament_values[tourney] = info['value']
            
    all_results = OrderedDict(ordered_placements)

    f = open('Data/tts_values.csv','a')
    for key in tournament_values:
        f.write('%s,%d\n' % (key,tournament_values[key]))
    f.close()
    
    return all_results

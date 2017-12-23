import json, os
import smashgg_api

link_h = 'https://api.smash.gg/tournament/'

API_URL = 'https://api.smash.gg'
TOURNAMENT_HEAD = 'https://api.smash.gg/tournament/'
GROUP_HEAD = 'https://api.smash.gg/phase_group/'

def omit_sponsor(tag):
    start = 0 if tag.rfind('| ') == -1 else tag.rfind('| ')+2
    return tag[start:].encode('ascii','replace')

#res is the json object
def use_event_entrant_data(res, option):
    pass

# tournament, event   OR   link
# reverse=boolean as an extra
def get_event_entrant_ids(*args, **kwargs):

    if len(args) == 1:
        link = smashgg_api.parse_url(args[0]) + '?expand=entrants'
    elif len(args) == 2:
        tournament = args[0]
        event = args[1]
        link = '%s%s/event/%s?expand[]=entrants' % (link_h, tournament, event)
    else:
        print 'Invalid number of arguments!!!'
        return
    
    reverse = kwargs['reverse'] if 'reverse' in kwargs else False
    players = {}

    for p in smashgg_api.get(link)['entrants']:
        start = 0 if p['name'].rfind('| ') == -1 else p['name'].rfind('| ')+2
        p_name =  p['name'][start:].encode('ascii','replace')
        if not reverse:
            players[p_name] = int(p['id'])
        else:
            players[int(p['id'])] = p_name
    return players

# tournament, event   OR   link
def get_event_num_phases(*args):
    if len(args) == 1:
        link = smashgg_api.parse_url(args[0]) + '?expand=phase'
    elif len(args) == 2:
        tournament = args[0]
        event = args[1]
        link = '%s%s/event/%s?expand[]=phase' % (link_h, tournament, event)
    else:
        print 'Invalid number of arguments!!!'
        return
    
    return len(smashgg_api.get(link)['phase'])
    
def get_event_bracket_groups(*args):
    if len(args) == 1:
        link = smashgg_api.parse_url(args[0]) + '?expand=groups'
    elif len(args) == 2:
        tournament = args[0]
        event = args[1]
        link = '%s%s/event/%s?expand[]=groups' % (link_h, tournament, event)
    else:
        print 'Invalid number of arguments!!!'
        return
    
    return smashgg_api.get(link)['groups']


def get_phase_group_sets(group_id):
    link = 'https://api.smash.gg/phase_group/%d?expand[]=sets' % (group_id)
    get_o = smashgg_api.get(link)
    sets = get_o['sets'] if 'sets' in get_o else []    
    sets_info = []
    
    for _set in sets:
        p1 = _set['entrant1Id']
        p2 = _set['entrant2Id']
        if p1 != None and p2 != None and _set['winnerId'] != None and _set['loserId'] != None:
            sets_info.append(_set)
    
    return sets_info


# tournament, event, player / link, player
def get_player_sets(*args):

    if len(args) == 2:
        player = args[1]
        groups = get_event_bracket_groups(args[0])
        ids = get_event_entrant_ids(args[0])
        tags = get_event_entrant_ids(args[0], reverse=True)
        num_phases = get_event_num_phases(args[0])
        p_id = ids[player]
    elif len(args) == 3:
        tournament = args[0]
        event = args[1]
        player = args[2]
        groups = get_event_bracket_groups(tournament, event)
        ids = get_event_entrant_ids(tournament, event)
        tags = get_event_entrant_ids(tournament, event, reverse=True)
        num_phases = get_event_num_phases(tournament, event)
        p_id = ids[player]
    else:
        print 'Invalid number of arguments!!!'
        return
    

    player_phases  = 0
    p_sets = {'path': [], 'wins': [], 'losses': []}

    for group in groups:
        if player_phases < num_phases:
            sets_info = get_phase_group_sets(group['id'])
            player_found = False
            for _set in sets_info:
                if _set['entrant1Id'] == p_id or _set['entrant2Id'] == p_id:
                    playerFound = True
                    p1 = player
                    if _set['entrant1Id'] == p_id:
                        p2 = omit_sponsor(tags[_set['entrant2Id']])
                        p1_score = _set['entrant1Score']
                        p2_score = _set['entrant2Score']
                    else:
                        p2 = omit_sponsor(tags[_set['entrant1Id']])
                        p1_score = _set['entrant2Score']
                        p2_score = _set['entrant1Score']
                        
                    winner = p1 if _set['winnerId'] == p_id else p2 
                    loser = p1 if _set['winnerId'] != p_id else p2 

                    #possibly use _set['round'] to order path
                    p_sets['path'].append((p2, 'W' if winner==p1 else 'L'))
                    set_dest = p_sets['wins'] if winner == p1 else p_sets['losses']
                    set_dest.append({
                        'p1': p1,
                        'p2': p2,
                        'Winner': winner,
                        'Loser': loser,
                        'p1_score': p1_score,
                        'p2_score': p2_score,
                        'path_pos': len(p_sets['path'])-1
                    })
                    
            player_phases += 1 if player_found else 0
            
    return p_sets


def get_mult_players_sets(*args):

    if len(args) == 2:
        players_in = args[1]
        groups = get_event_bracket_groups(args[0])
        ids = get_event_entrant_ids(args[0])
        tags = get_event_entrant_ids(args[0], reverse=True)
        num_phases = get_event_num_phases(args[0])
    elif len(args) == 3:
        tournament = args[0]
        event = args[1]
        players_in = args[2]
        groups = get_event_bracket_groups(tournament, event)
        ids = get_event_entrant_ids(tournament, event)
        tags = get_event_entrant_ids(tournament, event, reverse=True)
        num_phases = get_event_num_phases(tournament, event)
    else:
        print 'Invalid number of arguments!!!'
        return

    players = []
    
    for p in players_in:
        if p in ids:
            players.append(p)
    
    p_ids = [ids[player] for player in players]
    players_sets = {p: {'path': [], 'wins': [], 'losses': []} for p in players}
    players_phases = {p:0 for p in p_ids}
    
    for group in groups:

        #print group['id']
        
        sets_info = get_phase_group_sets(group['id'])

        players_found = {p:False for p in p_ids}
        
        for _set in sets_info:
            for p_id in p_ids:
                if players_phases[p_id] < num_phases:
                    if _set['entrant1Id'] == p_id or _set['entrant2Id'] == p_id:
                        players_found[p_id] = True
                        p1 = tags[p_id]
                        if _set['entrant1Id'] == p_id:
                            p2 = omit_sponsor(tags[_set['entrant2Id']])
                            p1_score = _set['entrant1Score']
                            p2_score = _set['entrant2Score']
                        else:
                            p2 = omit_sponsor(tags[_set['entrant1Id']])
                            p1_score = _set['entrant2Score']
                            p2_score = _set['entrant1Score']
                        #print p1,p2
                        winner = p1 if _set['winnerId'] == p_id else p2 
                        loser = p1 if _set['winnerId'] != p_id else p2 
                    
                        players_sets[p1]['path'].append((p2, 'W' if winner==p1 else 'L'))
                        
                        set_dest = players_sets[p1]['wins'] if winner == p1 else players_sets[p1]['losses']
                    
                        set_dest.append({
                            'p1': p1,
                            'p2': p2,
                            'Winner': winner,
                            'Loser': loser,
                            'p1_score': p1_score,
                            'p2_score': p2_score,
                            'path_pos': len(players_sets[p1]['path'])-1
                        })

        for id in p_ids:
            players_phases[id] += 1 if players_found[id] == True else 0 
            
    return players_sets


#print get_player_sets('super-smash-con-2017','wii-u-singles','ZeRo')

#print get_player_sets('evo-2017','super-smash-bros-for-wii-u','Mistake')

#w = get_mult_players_sets('https://smash.gg/tournament/super-smash-con-2017/events/wii-u-singles/brackets/144668/406414',['ZeRo','Nairo','MKLeo'])

#print w

'''
f = open('sets_output','w')
for x in w:
    f.write(x + ': ')
    f.write(str(w[x]))
    f.write('\n\n')
'''

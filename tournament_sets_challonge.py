import json
import challonge_api

def omit_character(tag):
    index = len(tag) if tag.find(' (') == -1 else tag.find(' (')
    return tag[:index]

def omit_sponsor(tag):
    start = 0 if tag.rfind('| ') == -1 else tag.rfind('| ')+2
    return tag[start:].encode('ascii','replace')


def get_entrant_ids(link,reverse=False):

    players = {}
    
    for p in challonge_api.get(link,'participants'):
        name = omit_sponsor(omit_character(p['participant']['name']))
        id = p['participant']['id']
        if not reverse:
            players[name] = int(id)
        else:
            players[int(id)] = name
    return players

    
def get_player_sets(link, player):

    sets = challonge_api.get(link,'matches')
    ids = get_entrant_ids(link)
    tags = get_entrant_ids(link,reverse=True)
    p_id = ids[player]

    p_sets = {'path':[], 'wins': [], 'losses': []}
    
    for _set in sets:
        id_1 = _set['match']['player1_id']
        id_2 = _set['match']['player2_id']
        if id_1 != None and id_2 != None:

            score = _set['match']['scores_csv'].split('-')
            id_1_score = score[0]
            id_2_score = score[1]
            
            if id_1 == p_id or id_2 == p_id:
                p1 = player
                if id_1 == p_id:
                    p2 = omit_sponsor(omit_character(tags[id_2]))
                    p1_score = id_1_score
                    p2_score = id_2_score
                else:
                    p2 = omit_sponsor(omit_character(tags[id_1]))
                    p1_score = id_2_score
                    p2_score = id_1_score

                winner = p1 if p_id == _set['match']['winner_id'] else p2
                loser = p1 if p_id != _set['match']['winner_id'] else p2

                p_sets['path'].append((p2,'W' if winner==p1 else 'L'))
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

    return p_sets

def get_mult_players_sets(link, players_in):

    sets = challonge_api.get(link,'matches')
    ids = get_entrant_ids(link)
    tags = get_entrant_ids(link,reverse=True)


    players = []
    
    for p in players_in:
        if p in ids:
            players.append(p)

    
    p_ids = [ids[player] for player in players]

    players_sets = {p:{'path':[], 'wins': [], 'losses': []} for p in players}
    
    for _set in sets:
        id_1 = _set['match']['player1_id']
        id_2 = _set['match']['player2_id']
        if id_1 != None and id_2 != None:

            for p_id in p_ids:
                if id_1 == p_id or id_2 == p_id:

                    score = _set['match']['scores_csv'].split('-')
                    id_1_score = score[0]
                    id_2_score = score[1]
                
                    p1 = tags[p_id]
                    if id_1 == p_id:
                        p2 = omit_sponsor(omit_character(tags[id_2]))
                        p1_score = id_1_score
                        p2_score = id_2_score
                    else:
                        p2 = omit_sponsor(omit_character(tags[id_1]))
                        p1_score = id_2_score
                        p2_score = id_1_score
                    
                    winner = p1 if p_id == _set['match']['winner_id'] else p2
                    loser = p1 if p_id != _set['match']['winner_id'] else p2

                    players_sets[p1]['path'].append((p2,'W' if winner==p1 else 'L'))
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

    return players_sets


#print get_mult_players_sets('http://challonge.com/Karisuma14T', ['9B','Taiheita','Kisha'])

#print get_player_sets('http://challonge.com/Sumabato19T','9B')

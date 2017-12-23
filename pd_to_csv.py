from collections import OrderedDict
import json, csv, xlsxwriter, re
from xlsxwriter.utility import xl_rowcol_to_cell as rc_to_cell


'''
More:


h2hs
Wins:
-Place (score)
Losses:
-Place (Score)


placings
Wins: (ppl)
Losses: (ppl)

'''


comments_on = False
notable = ['Mistake','Cosmos','Lima','False','Vinnie','Charliedaking','tyroy','Konga','Light','DarkShad','Zenyou','Ryuga','dyr','IxisNaugus','SuperGirlKels','Luhtie','Gluttony']

def valid_h2h(string):
    form = re.compile("^[0-9]+-[0-9]+$")
    if form.match(string):
        return True
    return False
        

def get_sets_res(p_info,p1,p2,res):
    if res != 'wins' and res != 'losses':
        print 'Bad input!'
        return
    data = p_info[p1]['sets'][res][p2] if p2 in p_info[p1]['sets'][res] else {}
    tally = OrderedDict()
    if 'when' in data:
        for place in data['when']:
            if str(place) in tally:
                tally[str(place)] += 1
            else:
                tally[str(place)] = 1
    res_string = ''
    for place in tally:
        res_string += '%s x%d\n' % (place, tally[place])
    return res_string[:-1]

    
def h2h_sheet(comments_on=False):

    with open('Data/players_info.json','r') as dt:
        p_info = json.load(dt) #, object_pairs_hook=OrderedDict)
    with open('Data/PGR_Players.json','r') as dt:
        pgr = json.load(dt, object_pairs_hook=OrderedDict)
        pgr_players = pgr['players']
        area_51 = pgr['area51']
    with open('Data/lower_tags.json','r') as dt:
        lower_tags = json.load(dt)
        
    pgr_list = [lower_tags[str(p).lower()] if str(p).lower() in lower_tags else str(p) for p in pgr_players] + [lower_tags[str(p).lower()] if str(p).lower() in lower_tags else str(p) for p in area_51]

    player_list = pgr_list + [lower_tags[p.lower()] for p in notable]

    #single_tag = {lower_tags[str(p).lower()]:str(p) if str(p).lower() in lower_tags else str(p) for p in pgr_players} + {lower_tags[str(p).lower()]:str(p) if str(p).lower() in lower_tags else str(p) for p in area_51}
    single_tag = {}
    for p in pgr_players:
        if str(p) in lower_tags:
            single_tag[str(lower_tags[str(p).lower()])] = str(p)
        else:
            single_tag[str(p)] = str(p)
    for p in area_51:
        if str(p) in lower_tags:
            single_tag[str(lower_tags[str(p).lower()])] = str(p)
        else:
            single_tag[str(p)] = str(p)
    for p in notable:
        single_tag[p] = p
    
    for p in p_info:
        if str(p) not in player_list:
            player_list.append(str(p))
            single_tag[str(p)] = str(p)
            
    comments = {}
            
    with open('Output/h2hs.csv','w') as csvfile:
        fieldnames = [None] + player_list
        w = csv.DictWriter(csvfile, fieldnames=fieldnames)
        w.writeheader()
        for p in player_list:
            row = {None:p}
            if p in p_info: #pgr players with no presence this season
                h2hs = p_info[p]['sets']['h2hs']
                for opp in h2hs:
                    if opp in player_list:
                        row[opp] = '%d-%d' % (h2hs[opp][0], h2hs[opp][1])
                        data_w = p_info[p]['sets']['wins'][opp] if opp in p_info[p]['sets']['wins'] else None
                        data_l = p_info[p]['sets']['losses'][opp] if opp in p_info[p]['sets']['losses'] else None
            w.writerow(row)

    wb = xlsxwriter.Workbook('Output/h2hs.xlsx')
    ws = wb.add_worksheet()
    
    red = wb.add_format({'bg_color': 'f4c7c3'}) 
    green = wb.add_format({'bg_color': 'b7e1cd'})
    yellow = wb.add_format({'bg_color': 'fce8b2'}) 
    gray = wb.add_format({'bg_color': '999999'})
    red2 = wb.add_format({'bg_color': 'ea9999'})
    blue = wb.add_format({'bg_color': 'a4c2f4'})
    yellow = wb.add_format({'bg_color': 'ffe599'})
    green2 = wb.add_format({'bg_color': 'b6d7a8'})
    purple = wb.add_format({'bg_color': 'd5a6bd'})
    ws.freeze_panes(1,1)
    ws.freeze_panes(1,1)
    
    with open('Output/h2hs.csv') as csvfile:
        sheet = list(csv.reader(csvfile))
        row = 0
        while row < len(sheet):
            col = 0
            while col < len(sheet[row]):
                if valid_h2h(sheet[row][col]):
                    s = sheet[row][col].split('-')
                    W = s[0]
                    L = s[1]
                    form = red if L > W else green if W > L else yellow
                    ws.write(row,col,sheet[row][col],form)
                    #comnents make it laggy
                    if comments_on:
                        p1 = sheet[row][0]
                        p2 = sheet[0][col]
                        p_wins = get_sets_res(p_info,p1,p2,'wins')
                        p_losses = get_sets_res(p_info,p1,p2,'losses')
                        score_info = 'Wins:\n%s\n\nLosses:\n%s' % (p_wins,p_losses)
                        ws.write_comment(rc_to_cell(row,col),score_info)
                elif row != 0 and row == col:
                    ws.write(row,col,sheet[row][col],gray)
                elif (row == 0) is not (col == 0) and (sheet[row][col] in pgr_players or single_tag[sheet[row][col]] in pgr_players):
                    ws.write(row,col,sheet[row][col],green2)
                elif (row == 0) is not (col == 0) and (sheet[row][col] in pgr_list or single_tag[sheet[row][col]] in pgr_list):
                    ws.write(row,col,sheet[row][col],purple)
                else:
                    ws.write(row,col,sheet[row][col])
                col +=1
            row += 1
        wb.close()
        
        
    return


def placings_sheet():

    with open('Data/Tournaments.json','r') as dt:
        tournaments = json.load(dt,object_pairs_hook=OrderedDict)
    with open('Data/players_info.json','r') as dt:
        p_info = json.load(dt) #, object_pairs_hook=OrderedDict)
    with open('Data/PGR_Players.json','r') as dt:
        pgr = json.load(dt, object_pairs_hook=OrderedDict)
        pgr_players = pgr['players']
        area_51 = pgr['area51']
    with open('Data/lower_tags.json','r') as dt:
        lower_tags = json.load(dt)
        
    pgr_list = [lower_tags[str(p).lower()] if str(p).lower() in lower_tags else str(p) for p in pgr_players] + [lower_tags[str(p).lower()] if str(p).lower() in lower_tags else str(p) for p in area_51] 
    player_list = pgr_list + [lower_tags[p.lower()] for p in notable]

    #single_tag = {lower_tags[str(p).lower()]:str(p) if str(p).lower() in lower_tags else str(p) for p in pgr_players} + {lower_tags[str(p).lower()]:str(p) if str(p).lower() in lower_tags else str(p) for p in area_51}
    single_tag = {}
    for p in pgr_players:
        if str(p) in lower_tags:
            single_tag[str(lower_tags[str(p).lower()])] = str(p)
        else:
            single_tag[str(p)] = str(p)
    for p in area_51:
        if str(p) in lower_tags:
            single_tag[str(lower_tags[str(p).lower()])] = str(p)
        else:
            single_tag[str(p)] = str(p)
    for p in notable:
        single_tag[p] = p
            
    for p in p_info:
        if str(p) not in player_list:
            player_list.append(str(p))
            single_tag[str(p)] = str(p)
            
    with open('Output/placements.csv','w') as csvfile:
        fieldnames = [None] + [t for t in tournaments]
        w = csv.DictWriter(csvfile,fieldnames=fieldnames)
        w.writeheader()
        for p in player_list:
            row = {None: p}
            if p in p_info: #inactive pgr members
                for place in p_info[p]['placings']:
                    row[place] = p_info[p]['placings'][place]
            w.writerow(row)


    '''
    1st: ffff00
    2nd: cccccc
    3rd: dc7407
    4th and beyond: b7e1cd
    '''

    wb = xlsxwriter.Workbook('Output/placements.xlsx')
    ws = wb.add_worksheet()
    
    bold = wb.add_format({'bold': True})
    first = wb.add_format({'bg_color': 'ffff00'}) 
    second = wb.add_format({'bg_color': 'cccccc'})
    third = wb.add_format({'bg_color': 'dc7407'})
    other = wb.add_format({'bg_color': 'b7e1cd'}) 
    green = wb.add_format({'bg_color': 'b6d7a8'})
    purple = wb.add_format({'bg_color': 'd5a6bd'})
    ws.freeze_panes(1,1)
    ws.freeze_panes(1,1)
    
    with open('Output/placements.csv') as csvfile:
        sheet = list(csv.reader(csvfile))
        row = 0
        while row < len(sheet):
            col = 0
            while col < len(sheet[row]):
                if row == 0:
                    ws.write(row,col,sheet[row][col],bold)
                elif (row == 0) is not (col == 0) and (sheet[row][col] in pgr_players or single_tag[sheet[row][col]] in pgr_players):
                    ws.write(row,col,sheet[row][col],green)
                elif (row == 0) is not (col == 0) and (sheet[row][col] in pgr_list or single_tag[sheet[row][col]] in pgr_list):
                    ws.write(row,col,sheet[row][col],purple)
                elif sheet[row][col] == '1st':
                    ws.write(row,col,sheet[row][col],first)
                elif sheet[row][col] == '2nd':
                    ws.write(row,col,sheet[row][col],second)
                elif sheet[row][col] == '3rd':
                    ws.write(row,col,sheet[row][col],third)
                elif sheet[row][col] != '' and col >= 1:
                    ws.write(row,col,sheet[row][col],other)
                else:
                    ws.write(row,col,sheet[row][col])
                col += 1
            row += 1
    return
    
h2h_sheet(comments_on)
placings_sheet()

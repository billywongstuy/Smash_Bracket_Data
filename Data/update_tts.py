# Google Sheets
# View > Show formulas

# copy the tournaments to a text file

import json
from collections import OrderedDict

f = open('12-02-17.txt','r')
r = f.read()

lines = r.split('\n')[:-1]

#info['smash.gg'] = OrderedDict()
#info['challonge'] = OrderedDict()

smashgg = []
challonge = []
tournaments = []


for line in lines:
    data = line.split(',')
    
    if 'challonge' not in data[0]:
        if 'overview' in data[0]:
            data[0] = data[0][12:-10]
        else:
            data[0] = (data[0][12:-1] + '/wii-u-singles')
    else:
        data[0] = data[0][12:-1]

    data[1] = data[1][1:-2]
    
    if data[1][-2:] == '**':
        tournaments.append((data[1][:-2],(data[0],'challonge')))
        #challonge.append((data[1][:-2],data[0]))   
    else:
        tournaments.append((data[1],(data[0],'smash.gg')))
        #smashgg.append((data[1],data[0]))

    #print data[1][-2:], data[1][:-2]

#smashgg = OrderedDict(smashgg)
#challonge = OrderedDict(challonge)

#info = OrderedDict([('smash.gg',smashgg),('challonge',challonge)])

info = OrderedDict(tournaments)
    
f.close()

with open('Tournaments.json','w') as fp:
    data = json.dump(info, fp)

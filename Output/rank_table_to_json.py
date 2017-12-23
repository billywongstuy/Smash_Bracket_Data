f = open('Data/pgrv3.csv','r')
r = f.read()

rows = r.split('\n')
rows = rows[1:-1]


content = '''{
    "players": {
'''

for row in rows:
    dat = row.split(',')
    #print dat[0], dat[1][3:]
    content += '\t"%s": %s,\n' % (dat[1][3:], dat[0]) 

f.close()


content += '''    }
}'''

print content

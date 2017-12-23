
def get_tts_vals():
    f = open('v3_tts_vals.csv','r')
    r = f.read()

    lines = r.split('\n')[:-1]
    
    tourneys = {}

    for line in lines:
        vals = line.split(',')
        tourneys[vals[0]] = vals[1]

    return tourneys

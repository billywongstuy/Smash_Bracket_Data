import urllib2, json, os, datetime
from urllib2 import HTTPError


url = 'https://api.smash.gg/tournament/super-smash-con-2017'

try:
    u = urllib2.urlopen(url)
except:
    u = {}
    print 'Error occured when retrieving data'


response = u.read()
res = json.loads( response )

print res['entities']['tournament']['name']

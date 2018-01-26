import urllib2, json

#includes parse
def get(url,query):

    name = url[url.find('challonge.com/')+len('challonge.com/'):]
    link = 'https://api.challonge.com/v1/tournaments/%s/%s.json?api_key=rX34ZcxUyDVs1jj6PV4lU5a6xvlOn5CD6TUMOQBt' % (name,query)
    
    try:
        u = urllib2.urlopen(link)
        response = u.read()
        return json.loads(response)
    except:
        u = {}
        print url
        print 'Error occured when retrieving data'
        return

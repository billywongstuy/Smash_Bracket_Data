import urllib2, json

def get(url):
    try:
        u = urllib2.urlopen(url)
        response = u.read()
        return json.loads(response)['entities']
    except:
        u = {}
        print url
        print 'Error occured when retrieving data'
        return


def parse_url(url):
    url = url.split('brackets')[0]
    url = url.replace('events','event')
    url = url.replace('smash.gg','api.smash.gg') if 'api' not in url else url
    if url[-1] == "/":
        url = url[:-1]
    return url

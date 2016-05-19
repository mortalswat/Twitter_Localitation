# Interesting Tools
# https://api.twitter.com/oauth/request_token

# import twitter
import twitter
import json
import requests
import urlparse
import oauth2
import datetime

from datetime import timedelta
from flask import Flask, request, render_template
from flask.ext.googlemaps import GoogleMaps
from flask.ext.googlemaps import Map

CONSUMER_KEY='OLDLHqzjpVgOndpKVOlv2Wt23'
CONSUMER_SECRET='y5q0NHmRRiTZZrcWcTnCgIiXBsU29FGUC2cqtcYGca9eADFZrk'
OAUTH_TOKEN = ""
OAUTH_TOKEN_SECRET = ""
    
consumer = ""
request_token = ""


def oauth_login():
    auth = twitter.oauth.OAuth(OAUTH_TOKEN, OAUTH_TOKEN_SECRET, CONSUMER_KEY, CONSUMER_SECRET)

    twitter_api = twitter.Twitter(auth=access_token)
    return twitter_api


def geo(tw,ht):
    query = tw.search.tweets(q=('#'+ht),count=100)
    
    listado=[]
    
    for resultado in query["statuses"]:
        # only process a result if it has a geolocation
        if resultado["place"]:
            #(resultado["place"]["bounding_box"]["coordinates"][0])
            momento = datetime.datetime.strptime(resultado["created_at"], '%a %b %d %H:%M:%S +0000 %Y') + timedelta(hours=1)
            latitud = 0
            longitud = 0
            for e in resultado["place"]["bounding_box"]["coordinates"][0]:
                latitud += e[0]
                longitud += e[1]
            latitud = latitud/len(resultado["place"]["bounding_box"]["coordinates"][0])
            longitud = longitud/len(resultado["place"]["bounding_box"]["coordinates"][0])
            
            momento = momento + datetime.timedelta(hours=1)
            listado.append({"id":resultado["id"], "lugar" : resultado["place"]["full_name"], "momento" : momento, "latitud" : latitud, "longitud" : longitud, "usuario":resultado["user"]})
            
    return listado


def login1():
    global consumer
    global request_token
    
    request_token_url='https://api.twitter.com/oauth/request_token'
    authorize_url='https://api.twitter.com/oauth/authorize'

    consumer=oauth2.Consumer(CONSUMER_KEY,CONSUMER_SECRET)
    client=oauth2.Client(consumer)
    resp, content = client.request(request_token_url, "GET")

    if resp['status'] != '200':
        raise Exception("Invalid response %s." % resp['status'])

    request_token = dict(urlparse.parse_qsl(content))
    url = "%s?oauth_token=%s" % (authorize_url, request_token['oauth_token'])

    return render_template('twitter.html', url=url)


def login2(pin):
    global consumer
    global request_token
    global OAUTH_TOKEN
    global OAUTH_TOKEN_SECRET

    access_token_url='https://api.twitter.com/oauth/access_token'

    token = oauth2.Token(request_token['oauth_token'],request_token['oauth_token_secret'])
     
    token.set_verifier(pin)
    client = oauth2.Client(consumer, token)

    resp, content = client.request(access_token_url, "POST")
    access_token = dict(urlparse.parse_qsl(content))

    OAUTH_TOKEN = access_token["oauth_token"]
    OAUTH_TOKEN_SECRET = access_token["oauth_token_secret"]

    return friends()


def friends():
    listado = geo(oauth_login(),"ElDesGobiernoDelPP")
    l={}

    for e in listado:
        l.update({e['usuario']['profile_image_url']:[(e['longitud'],e['latitud'])]})

    mapa = Map(
        identifier="view-side",
        lat=40.3450396,
        lng=-3.6517684,
        zoom=6,
        markers=l,
        style="height:600px;width:800px;margin:0;"
    )

    return render_template('mapa.html', mapa=mapa, tag=tag, listado=listado)



app = Flask(__name__)
GoogleMaps(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/twitter/')
def twitter():
    return login1()

@app.route('/twitter/pin/', methods=['POST'])
def twitterpin():
    return login2(request.form['pin'])

if __name__ == "__main__":
    app.run(debug=True)
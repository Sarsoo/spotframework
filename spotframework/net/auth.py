import os
import requests
from base64 import b64encode

client_id = os.environ['SPOTCLIENT']
client_secret = os.environ['SPOTSECRET']
user_access_token = os.environ['SPOTACCESS']
user_refresh_token = os.environ['SPOTREFRESH']

#This sets up the https connection
#we need to base 64 encode it
#and then decode it to acsii as python 3 stores it as a byte string
def refreshToken():

    idsecret = b64encode(bytes(client_id + ':' + client_secret, "utf-8")).decode("ascii")
    headers = { 'Authorization' : 'Basic %s' %  idsecret }

    data = {"grant_type": "refresh_token", "refresh_token": user_refresh_token}
    
    req = requests.post('https://accounts.spotify.com/api/token', data = data, headers = headers )

    if req.status_code == 200:
        user_access_token = req.json()['access_token']

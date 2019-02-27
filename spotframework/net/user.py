import os
import requests
from base64 import b64encode

client_id = os.environ['SPOTCLIENT']
client_secret = os.environ['SPOTSECRET']

class User:

    def __init__(self):
        self.access_token = os.environ['SPOTACCESS']
        self.refresh_token = os.environ['SPOTREFRESH']

    def refreshToken(self):
        
        idsecret = b64encode(bytes(client_id + ':' + client_secret, "utf-8")).decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  idsecret }

        data = {"grant_type": "refresh_token", "refresh_token": self.refresh_token}
    
        req = requests.post('https://accounts.spotify.com/api/token', data = data, headers = headers )
   
        print(req.status_code)
        print(req.text)

        self.access_token = req.json()['access_token']

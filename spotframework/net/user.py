import os
import requests
from base64 import b64encode

client_id = os.environ['SPOTCLIENT']
client_secret = os.environ['SPOTSECRET']

class User:

    def __init__(self):
        self.access_token = os.environ['SPOTACCESS']
        self.refresh_token = os.environ['SPOTREFRESH']
        
        self.refreshToken()

        self.username = self.getInfo()['id']

    def refreshToken(self):
        
        idsecret = b64encode(bytes(client_id + ':' + client_secret, "utf-8")).decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  idsecret }

        data = {"grant_type": "refresh_token", "refresh_token": self.refresh_token}
    
        req = requests.post('https://accounts.spotify.com/api/token', data = data, headers = headers )
   
        #print(req.status_code)
        #print(req.text)
        
        if req.status_code is 200:
            self.access_token = req.json()['access_token']

    def getInfo(self):
        
        headers = { 'Authorization' : 'Bearer %s' %  self.access_token }

        req = requests.get('https://api.spotify.com/v1/me', headers = headers)
        return req.json()

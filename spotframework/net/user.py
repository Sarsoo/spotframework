import requests
from base64 import b64encode


class User:

    def __init__(self, client_id, client_secret, access_token, refresh_token):
        self.accesstoken = access_token
        self.refreshtoken = refresh_token

        self.client_id = client_id
        self.client_secret = client_secret

        self.refresh_token()

        self.username = self.get_info()['id']

    def refresh_token(self):
        
        idsecret = b64encode(bytes(self.client_id + ':' + self.client_secret, "utf-8")).decode("ascii")
        headers = {'Authorization': 'Basic %s' % idsecret}

        data = {"grant_type": "refresh_token", "refresh_token": self.refreshtoken}
    
        req = requests.post('https://accounts.spotify.com/api/token', data=data, headers=headers)
   
        if req.status_code is 200:
            self.accesstoken = req.json()['access_token']

    def get_info(self):
        
        headers = {'Authorization': 'Bearer %s' % self.accesstoken}

        req = requests.get('https://api.spotify.com/v1/me', headers=headers)
        return req.json()

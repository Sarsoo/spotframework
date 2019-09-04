import requests
from spotframework.model.user import User
from base64 import b64encode
import logging

logger = logging.getLogger(__name__)


class NetworkUser(User):

    def __init__(self, client_id, client_secret, access_token, refresh_token):
        super().__init__('')

        self.accesstoken = access_token
        self.refreshtoken = refresh_token

        self.client_id = client_id
        self.client_secret = client_secret

        self.refresh_token()
        self.refresh_info()

    def refresh_token(self):
        
        idsecret = b64encode(bytes(self.client_id + ':' + self.client_secret, "utf-8")).decode("ascii")
        headers = {'Authorization': 'Basic %s' % idsecret}

        data = {"grant_type": "refresh_token", "refresh_token": self.refreshtoken}
    
        req = requests.post('https://accounts.spotify.com/api/token', data=data, headers=headers)
   
        if 200 <= req.status_code < 300:
            logger.debug('token refreshed')
            self.accesstoken = req.json()['access_token']
        else:
            logger.error(f'http error {req.status_code}')

    def refresh_info(self):
        info = self.get_info()

        if info.get('display_name', None):
            self.display_name = info['display_name']

        if info.get('external_urls', None):
            if info['external_urls'].get('spotify', None):
                self.ext_spotify = info['external_urls']['spotify']

        if info.get('href', None):
            self.href = info['href']

        if info.get('id', None):
            self.username = info['id']

        if info.get('uri', None):
            self.uri = info['uri']

    def get_info(self):
        
        headers = {'Authorization': 'Bearer %s' % self.accesstoken}

        req = requests.get('https://api.spotify.com/v1/me', headers=headers)

        if 200 <= req.status_code < 300:
            logger.debug(f'retrieved {req.status_code}')
            return req.json()
        else:
            logger.error(f'http error {req.status_code}')

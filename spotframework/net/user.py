from __future__ import annotations
import requests
from spotframework.model.user import PublicUser
from spotframework.util.console import Color
from dataclasses import dataclass, field
from base64 import b64encode
import logging
import time
from typing import Optional, List
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


@dataclass
class NetworkUser:

    access_token: str
    refresh_token: str

    client_id: str
    client_secret: str

    user: PublicUser = field(default=None, init=False)

    last_refreshed: datetime = field(default=None, init=False)
    token_expiry: datetime = field(default=None, init=False)

    on_refresh: List = field(default_factory=list, init=False)

    refresh_counter: int = field(default=0, init=False)

    def refresh_access_token(self) -> NetworkUser:

        if self.refresh_token is None:
            raise NameError('no refresh token to query')

        if self.client_id is None:
            raise NameError('no client id')

        if self.client_secret is None:
            raise NameError('no client secret')
        
        idsecret = b64encode(bytes(self.client_id + ':' + self.client_secret, "utf-8")).decode("ascii")
        headers = {'Authorization': 'Basic %s' % idsecret}

        data = {"grant_type": "refresh_token", "refresh_token": self.refresh_token}

        now = datetime.utcnow()
        req = requests.post('https://accounts.spotify.com/api/token', data=data, headers=headers)
   
        if 200 <= req.status_code < 300:
            logger.debug('token refreshed')
            resp = req.json()
            self.access_token = resp['access_token']
            if resp.get('refresh_token', None):
                self.refresh_token = resp['refresh_token']
            self.token_expiry = resp['expires_in']
            self.last_refreshed = now
            for func in self.on_refresh:
                func(self)
        else:

            if req.status_code == 429:
                retry_after = req.headers.get('Retry-After', None)

                if retry_after:
                    logger.warning(f'rate limit reached: retrying in {retry_after} seconds')
                    time.sleep(int(retry_after) + 1)
                    return self.refresh_access_token()
                else:
                    logger.error('rate limit reached: cannot find Retry-After header')

            else:
                error_text = req.json().get('error', 'n/a')
                error_description = req.json().get('error_description', 'n/a')
                logger.error(f'get {req.status_code} {error_text} - {error_description}')

        return self

    def refresh_info(self) -> None:
        self.user = PublicUser(**self.get_info())

    def get_info(self) -> Optional[dict]:
        
        headers = {'Authorization': 'Bearer %s' % self.access_token}

        req = requests.get('https://api.spotify.com/v1/me', headers=headers)

        if 200 <= req.status_code < 300:
            logger.debug(f'retrieved {req.status_code}')
            return req.json()
        else:

            if req.status_code == 429:
                retry_after = req.headers.get('Retry-After', None)

                if retry_after:
                    logger.warning(f'rate limit reached: retrying in {retry_after} seconds')
                    time.sleep(int(retry_after) + 1)
                    return self.get_info()
                else:
                    logger.error('rate limit reached: cannot find Retry-After header')

            elif req.status_code == 401:
                logger.warning('access token expired, refreshing')
                self.refresh_access_token()
                if self.refresh_counter < 5:
                    self.refresh_counter += 1
                    return self.get_info()
                else:
                    self.refresh_counter = 0
                    logger.critical('refresh token limit (5) reached')

            else:
                error = req.json().get('error', None)
                if error:
                    message = error.get('message', 'n/a')
                    logger.error(f'{req.status_code} {message}')
                else:
                    logger.error(f'{req.status_code} no error object found')

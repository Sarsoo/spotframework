import requests
from . import const

limit = 50

def getPlaylists(user, offset = 0):

    headers = {'Authorization': 'Bearer ' + user.access_token}
    
    playlists = []
    
    params = {'offset': offset, 'limit': limit}
    req = requests.get(const.api_url + 'me/playlists', params = params, headers = headers)
    
    print(req.text)

    if req.status_code == 200:
    
        print(req.text)

        resp = req.json()

        playlists = playlists + resp['items']
    
        if resp['next']:
            playlists += getPlaylists(user, offset + limit)

        print(req.text)        

        return playlists

    else:
        return None

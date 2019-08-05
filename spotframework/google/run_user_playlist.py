from google.cloud import firestore

import datetime

from spotframework.engine.playlistengine import PlaylistEngine
from spotframework.engine.filter.shuffle import Shuffle
from spotframework.engine.filter.sortreversereleasedate import SortReverseReleaseDate
from spotframework.engine.filter.deduplicatebyid import DeduplicateByID

from spotframework.net.network import Network
from spotframework.net.user import User

db = firestore.Client()

captured_playlists = []


def run_user_playlist(username, playlist_name):

    users = [i for i in db.collection(u'spotify_users').where(u'username', u'==', username).stream()]

    if len(users) == 1:

        user_dict = users[0].to_dict()

        playlist_collection = db.collection(u'spotify_users', u'{}'.format(users[0].id), 'playlists')

        playlists = [i for i in playlist_collection.where(u'name', u'==', playlist_name).stream()]

        if len(playlists) == 1:

            playlist_dict = playlists[0].to_dict()

            if playlist_dict['playlist_id'] is None:
                raise Exception('no playlist id to populate')

            if len(playlist_dict['parts']) == 0 and len(playlist_dict['playlist_references']) == 0:
                raise Exception('no playlists to use for creation')

            spotify_keys = db.document('key/spotify').get().to_dict()

            net = Network(User(spotify_keys['clientid'],
                               spotify_keys['clientsecret'],
                               user_dict['access_token'],
                               user_dict['refresh_token']))

            engine = PlaylistEngine(net)
            engine.load_user_playlists()

            processors = [DeduplicateByID()]

            if playlist_dict['shuffle'] is True:
                processors.append(Shuffle())
            else:
                processors.append(SortReverseReleaseDate())

            global captured_playlists
            captured_playlists = []

            submit_parts = playlist_dict['parts'] + generate_parts(users[0].id, playlist_dict['name'])

            submit_parts = [i for i in {j for j in submit_parts}]

            if playlist_dict['type'] == 'recents':
                boundary_date = datetime.datetime.now() - datetime.timedelta(days=int(playlist_dict['day_boundary']))
                tracks = engine.get_recent_playlist(boundary_date,
                                                    submit_parts,
                                                    processors,
                                                    include_recommendations=playlist_dict['include_recommendations'],
                                                    recommendation_limit=int(playlist_dict['recommendation_sample']))
            else:
                tracks = engine.make_playlist(submit_parts,
                                              processors,
                                              include_recommendations=playlist_dict['include_recommendations'],
                                              recommendation_limit=int(playlist_dict['recommendation_sample']))

            engine.execute_playlist(tracks, playlist_dict['playlist_id'])
            engine.change_description(sorted(submit_parts), playlist_dict['playlist_id'])

        else:
            raise Exception('multiple/no playlists found')

    else:
        raise Exception('multiple/no user(s) found')


def generate_parts(user_id, name):

    playlist_doc = [i.to_dict() for i in
                    db.document(u'spotify_users/{}'.format(user_id))
                    .collection(u'playlists')
                    .where(u'name', '==', name).stream()][0]

    return_parts = playlist_doc['parts']

    captured_playlists.append(name)

    for i in playlist_doc['playlist_references']:
        if i not in captured_playlists:
            return_parts += generate_parts(user_id, i)

    return return_parts

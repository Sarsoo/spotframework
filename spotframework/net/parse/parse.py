from spotframework.model.artist import SpotifyArtist
from spotframework.model.album import SpotifyAlbum
from spotframework.model.track import Track, SpotifyTrack, PlaylistTrack, PlayedTrack
from spotframework.model.playlist import SpotifyPlaylist
from spotframework.model.user import User
from spotframework.model.service import Context, CurrentlyPlaying, Device
import datetime
from typing import Union


def parse_artist(artist_dict) -> SpotifyArtist:

    name = artist_dict.get('name', None)

    href = artist_dict.get('href', None)
    uri = artist_dict.get('uri', None)

    genres = artist_dict.get('genres', None)
    popularity = artist_dict.get('popularity', None)

    if name is None:
        raise KeyError('artist name not found')

    return SpotifyArtist(name,
                         href=href,
                         uri=uri,

                         genres=genres,
                         popularity=popularity)


def parse_album(album_dict) -> SpotifyAlbum:

    name = album_dict.get('name', None)
    if name is None:
        raise KeyError('album name not found')

    artists = [parse_artist(i) for i in album_dict.get('artists', [])]

    href = album_dict.get('href', None)
    uri = album_dict.get('uri', None)

    genres = album_dict.get('genres', None)
    tracks = [parse_track(i) for i in album_dict.get('tracks', [])]

    release_date = album_dict.get('release_date', None)
    release_date_precision = album_dict.get('release_date_precision', None)

    label = album_dict.get('label', None)
    popularity = album_dict.get('popularity', None)

    return SpotifyAlbum(name=name,
                        artists=artists,

                        href=href,
                        uri=uri,

                        genres=genres,
                        tracks=tracks,

                        release_date=release_date,
                        release_date_precision=release_date_precision,

                        label=label,
                        popularity=popularity)


def parse_track(track_dict) -> Union[Track, SpotifyTrack, PlayedTrack]:

    if 'track' in track_dict:
        track = track_dict.get('track', None)
    else:
        track = track_dict

    name = track.get('name', None)
    if name is None:
        raise KeyError('track name not found')

    if track.get('album', None):
        album = parse_album(track['album'])
    else:
        album = None

    artists = [parse_artist(i) for i in track.get('artists', [])]

    href = track.get('href', None)
    uri = track.get('uri', None)

    disc_number = track.get('disc_number', None)
    duration_ms = track.get('duration_ms', None)
    explicit = track.get('explicit', None)
    is_playable = track.get('is_playable', None)

    popularity = track.get('popularity', None)

    added_by = parse_user(track_dict.get('added_by')) if track_dict.get('added_by', None) else None
    added_at = track_dict.get('added_at', None)
    if added_at:
        added_at = datetime.datetime.strptime(added_at, '%Y-%m-%dT%H:%M:%S%z')
    is_local = track_dict.get('is_local', None)

    played_at = track_dict.get('played_at', None)
    if played_at:
        played_at = datetime.datetime.strptime(played_at, '%Y-%m-%dT%H:%M:%S.%f%z')
    context = track_dict.get('context', None)
    if context:
        context = parse_context(context)

    if added_at or added_by or is_local:
        return PlaylistTrack(name=name,
                             album=album,
                             artists=artists,

                             added_at=added_at,
                             added_by=added_by,
                             is_local=is_local,

                             href=href,
                             uri=uri,

                             disc_number=disc_number,
                             duration_ms=duration_ms,
                             explicit=explicit,
                             is_playable=is_playable,

                             popularity=popularity)
    elif played_at or context:
        return PlayedTrack(name=name,
                           album=album,
                           artists=artists,

                           href=href,
                           uri=uri,

                           disc_number=disc_number,
                           duration_ms=duration_ms,
                           explicit=explicit,
                           is_playable=is_playable,

                           popularity=popularity,
                           played_at=played_at,
                           context=context)
    else:
        return SpotifyTrack(name=name,
                            album=album,
                            artists=artists,

                            href=href,
                            uri=uri,

                            disc_number=disc_number,
                            duration_ms=duration_ms,
                            explicit=explicit,
                            is_playable=is_playable,

                            popularity=popularity)


def parse_user(user_dict) -> User:
    display_name = user_dict.get('display_name', None)

    spotify_id = user_dict.get('id', None)
    href = user_dict.get('href', None)
    uri = user_dict.get('uri', None)

    return User(spotify_id,
                href=href,
                uri=uri,
                display_name=display_name)


def parse_playlist(playlist_dict) -> SpotifyPlaylist:

    collaborative = playlist_dict.get('collaborative', None)

    ext_spotify = None
    if playlist_dict.get('external_urls', None):
        if playlist_dict['external_urls'].get('spotify', None):
            ext_spotify = playlist_dict['external_urls']['spotify']

    href = playlist_dict.get('href', None)
    description = playlist_dict.get('description', None)

    name = playlist_dict.get('name', None)

    if playlist_dict.get('owner', None):
        owner = parse_user(playlist_dict.get('owner'))
    else:
        owner = None

    public = playlist_dict.get('public', None)
    uri = playlist_dict.get('uri', None)

    return SpotifyPlaylist(uri=uri,
                           name=name,
                           owner=owner,
                           description=description,
                           href=href,
                           collaborative=collaborative,
                           public=public,
                           ext_spotify=ext_spotify)


def parse_context(context_dict) -> Context:
    return Context(object_type=context_dict['type'],
                   href=context_dict['href'],
                   external_spot=context_dict['external_urls']['spotify'],
                   uri=context_dict['uri'])


def parse_currently_playing(play_dict) -> CurrentlyPlaying:
    return CurrentlyPlaying(context=parse_context(play_dict['context']) if play_dict['context'] is not None else None,
                            timestamp=datetime.datetime.fromtimestamp(play_dict['timestamp']/1000),
                            progress_ms=play_dict['progress_ms'],
                            is_playing=play_dict['is_playing'],
                            track=parse_track(play_dict['item']),
                            device=parse_device(play_dict['device']),
                            shuffle=play_dict['shuffle_state'],
                            repeat=play_dict['repeat_state'],
                            currently_playing_type=play_dict['currently_playing_type'])


def parse_device(device_dict) -> Device:
    return Device(device_id=device_dict['id'],
                  is_active=device_dict['is_active'],
                  is_private_session=device_dict['is_private_session'],
                  is_restricted=device_dict['is_restricted'],
                  name=device_dict['name'],
                  object_type=Device.DeviceType[device_dict['type'].upper()],
                  volume=device_dict['volume_percent'])


from spotframework.model.artist import Artist, SpotifyArtist
from spotframework.model.album import Album, SpotifyAlbum
from spotframework.model.track import Track, SpotifyTrack, PlaylistTrack
from spotframework.model.playlist import Playlist
from spotframework.model.user import User


def parse_artist(artist_dict) -> Artist:

    name = artist_dict.get('name', None)

    href = artist_dict.get('href', None)
    spotify_id = artist_dict.get('id', None)
    uri = artist_dict.get('uri', None)

    genres = artist_dict.get('genres', None)
    popularity = artist_dict.get('popularity', None)

    if name is None:
        raise KeyError('artist name not found')

    return SpotifyArtist(name,
                         href=href,
                         spotify_id=spotify_id,
                         uri=uri,

                         genres=genres,
                         popularity=popularity)


def parse_album(album_dict) -> Album:

    name = album_dict.get('name', None)
    if name is None:
        raise KeyError('album name not found')

    artists = [parse_artist(i) for i in album_dict.get('artists', [])]

    href = album_dict.get('href', None)
    spotify_id = album_dict.get('id', None)
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
                        spotify_id=spotify_id,
                        uri=uri,

                        genres=genres,
                        tracks=tracks,

                        release_date=release_date,
                        release_date_precision=release_date_precision,

                        label=label,
                        popularity=popularity)


def parse_track(track_dict) -> Track:

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

    # print(album.name)

    artists = [parse_artist(i) for i in track.get('artists', [])]

    href = track.get('href', None)
    spotify_id = track.get('id', None)
    uri = track.get('uri', None)

    disc_number = track.get('disc_number', None)
    duration_ms = track.get('duration_ms', None)
    explicit = track.get('explicit', None)
    is_playable = track.get('is_playable', None)

    popularity = track.get('popularity', None)

    added_by = parse_user(track_dict.get('added_by')) if track_dict.get('added_by', None) else None
    added_at = track_dict.get('added_at', None)
    is_local = track_dict.get('is_local', None)

    # print(album.name)

    if added_at or added_by or is_local:
        return PlaylistTrack(name=name,
                             album=album,
                             artists=artists,

                             added_at=added_at,
                             added_by=added_by,
                             is_local=is_local,

                             href=href,
                             spotify_id=spotify_id,
                             uri=uri,

                             disc_number=disc_number,
                             duration_ms=duration_ms,
                             explicit=explicit,
                             is_playable=is_playable,

                             popularity=popularity)
    else:
        return SpotifyTrack(name=name,
                            album=album,
                            artists=artists,

                            href=href,
                            spotify_id=spotify_id,
                            uri=uri,

                            disc_number=disc_number,
                            duration_ms=duration_ms,
                            explicit=explicit,
                            is_playable=is_playable,

                            popularity=popularity)


def parse_user(user_dict):
    display_name = user_dict.get('display_name', None)

    spotify_id = user_dict.get('id', None)
    href = user_dict.get('href', None)
    uri = user_dict.get('uri', None)

    return User(spotify_id,
                href=href,
                uri=uri,
                display_name=display_name)


def parse_playlist(playlist_dict):

    collaborative = playlist_dict.get('collaborative', None)

    ext_spotify = None
    if playlist_dict.get('external_urls', None):
        if playlist_dict['external_urls'].get('spotify', None):
            ext_spotify = playlist_dict['external_urls']['spotify']

    href = playlist_dict.get('href', None)
    playlist_id = playlist_dict.get('id', None)
    description = playlist_dict.get('description', None)

    name = playlist_dict.get('name', None)

    if playlist_dict.get('owner', None):
        owner = parse_user(playlist_dict.get('owner'))
    else:
        owner = None

    public = playlist_dict.get('public', None)
    uri = playlist_dict.get('uri', None)

    return Playlist(playlistid=playlist_id,
                    name=name,
                    owner=owner,
                    description=description,
                    href=href,
                    uri=uri,
                    collaborative=collaborative,
                    public=public,
                    ext_spotify=ext_spotify)

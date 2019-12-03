spotframework
===============

*scripting framework for interacting with the spotify web api*

* **alarm**

daily script which finds this months playlist (eg. 'may 19') and starts playback on a specified device id. if the monthly playlist can't be found
a fallback spotify uri is used.

the script is conditionally run after receiving a response from a ping sent to a phone's ip so the scipt is only run when i'm at home.
as phones won't typically respond to pings unless the screen is on multiple pings are sent and the script is scheduled for the same time as my mobile alarm

* **backup**

script to pull all user owned playlists and backup each to a separate csv file at the specified path

* **generate playlists**

my spotify playlists are quite granular for different sub genres, this script takes groups of playlists and genereates one "super-playlist".
took inspiriation from my main use of Paul Lamere's [smarter playlists](http://smarterplaylists.playlistmachinery.com/) 

by default playlists are reverse release date sorted, adding a shuffle tag to the config will do so.

example config schema:

```json
{
  "playlists": [
    {
      "name": "ELECTRONIC",
      "id": "{spotify playlist id}",
      "playlists": [
        "house",
        "garage",
        "jungle",
        ...
      ]
    },
    {
      "name": "METAL",
      "id": "{spotify playlist id}",
      "shuffle": true,
      "playlists": [
        "metal",
        "death metal",
        "black metal",
        ...
      ]
    },
    ...
```

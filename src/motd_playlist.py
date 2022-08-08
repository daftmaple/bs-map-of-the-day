import json
import os

import motd_db

def create_playlist(active=False):
    URL_FORMAT = "{}?active={}"

    playlist = {
        "playlistTitle": "Map of the Day (Active)",
        "playlistAuthor": "Map of the Day",
        "customData": {
            "syncUrl": URL_FORMAT.format(os.environ["BS_MOTD_SYNC_URL"], "true" if active else "false")
        },
        "songs": []
    }

    lbs = motd_db.get_active_leaderboards()
    if active == False:
        playlist["playlistTitle"] = "Map of the Day (All)"
        lbs = motd_db.get_old_leaderboards() + lbs # Attaching historical to the top

    for lb in lbs:
        playlist["songs"].append(leaderboard_to_json(lb))

    return playlist

def create_playlist_response(active=False):
    playlist = create_playlist(active)
    playlist_bytes = json.dumps(playlist, indent=2).encode('utf-8')

    return playlist_bytes

def leaderboard_to_json(lb):
    json = {
        "songName": lb["song_name"],
        "levelAuthorName": lb["song_mapper"],
        "hash": lb["song_hash"],
        "difficulties": [
            {
                "characteristic": lb["map_mode"],
                "name": lb["map_diff"]
            }
        ]
    }

    return json
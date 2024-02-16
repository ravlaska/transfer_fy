import requests
import os
import argparse
import ast

from playlists_parser import playlist_loader

# Main function
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("userId", help="User ID")
    parser.add_argument("accessToken", help="Access Token")
    parser.add_argument("sessionId", help="ID of session")
    parser.add_argument("playNames", help="Playlists names")
    args = parser.parse_args()

    # authentication header
    auth_head = {
        'Authorization': f'Bearer {args.accessToken}',
        'Content-Type': 'application/json'
    }

    # payload
    tracks_payload = {"uris": []}

    # creating variables for data
    playdir = f"uploads/{args.sessionId}"
    playlist_selected_names = ast.literal_eval(args.playNames)
    playlists_data = playlist_loader(playdir)
    playlist_name = []
    playlist_tracks = []

    # extracting data
    for item in playlists_data:
        if item[0] in playlist_selected_names:
            playlist_name.append(item[0])
            playlist_tracks.append(item[1:])

    # iterating through playlists
    for idx, upname in enumerate(playlist_name):
        tracks_payload['uris'].extend(track for track in playlist_tracks[idx]) # adding tracks to URIs
        playlist_payload = {"name": upname} # adding playlist name

        # creating playlist
        playlist_create = requests.post(f"https://api.spotify.com/v1/users/{args.userId}/playlists", headers=auth_head, json=playlist_payload)
        # retrieving created playlist ID
        playlist_json = playlist_create.json()
        playlist_id = playlist_json['id'] 

        # adding tracks to playlist
        requests.post(f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks", headers=auth_head, json=tracks_payload)

# default run
if __name__ == "__main__":
    main()
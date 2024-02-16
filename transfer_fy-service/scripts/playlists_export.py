import requests
import re
import os
import json
import time
import argparse
import zipfile
import shutil
import ast

# Exporting json file
def export_playlists(data, outdir, output):
    # dumping json data to variable
    json_out = json.dumps(data, sort_keys=False, indent=4)
    
    # saving data to JSON file
    with open(str(outdir) + str(output), 'w', encoding='utf-8') as json_export:
        json_export.write(json_out)

# Obtaining tracks on playlists
def get_playlist(playlist_id, playlist_name, header_uni_auth, outdir):
    while True:
        # requesting tracklist in single playlist
        response_track_list = requests.get(f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks', headers=header_uni_auth)
        if response_track_list.status_code == 200:
            break
        else:
            time.sleep(3)

    # creating json tracklist
    tracklist = {
        "name": playlist_name,
        "id": playlist_id,
        "tracks": []
        }
    tracks = response_track_list.json()['items'] # extracting tracks
    for track in tracks:
        tracklist['tracks'].append({
                "name": track['track']['name'],
                "album": track['track']['album']['name'],
                # "artists": track['track']['artists']['name'],
                "artists": [artist["name"] for artist in track['track']['artists']],
                "uri_track": track['track']['uri']
            })
    restricted_chars_pattern = r'[<>:"/\\|?*\0]'
    playlist_name = re.sub(restricted_chars_pattern, '', playlist_name) # check if name contains restricted chars
    export_playlists(tracklist, outdir, f"{playlist_name} [{playlist_id}].json") # exporting tracklist into file

# Compressing playlists jsons
def playlists_compress(userdir, jsondir, userId):
    # get all files in playlist directory
    files = [os.path.join(jsondir, f) for f in os.listdir(jsondir) if os.path.isfile(os.path.join(jsondir, f))]

    # create a zip file
    with zipfile.ZipFile(userdir + 'playlists_' + userId + '.zip', 'w') as zipf:
        for file in files:
            zipf.write(file, os.path.basename(file))
    
    # remove directory with playlists
    shutil.rmtree(jsondir)

# Main function
def main():
    # parsing input arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("userId", help="User ID")
    parser.add_argument("sessionId", help="ID of session")
    parser.add_argument("access_token", help="Access Token")
    parser.add_argument("playlists_dump", help="Playlists IDs")
    args = parser.parse_args()

    # directory handling
    userdir = f"files/{args.sessionId}/" # defining output directory
    jsondir = userdir + '/playlists/'   
    if not os.path.exists(jsondir):
        os.makedirs(jsondir)

    header_auth = {'Authorization': f'Bearer {args.access_token}'} # creating authentication header with token

    playlists_dump = ast.literal_eval(args.playlists_dump)
    playlists_names = []
    playlists_ids = []

    for idx, element in enumerate(playlists_dump):
        pids, pnames = element.split(' | ', 1)
        playlists_ids.append(pids)
        playlists_names.append(pnames)

    # iterating through playlists
    for idx, playid in enumerate(playlists_ids):
        get_playlist(playid, playlists_names[idx], header_auth, jsondir) # obtaining playlists one by one

    # compressing playlists jsons to zip
    playlists_compress(userdir, jsondir, args.userId)

# default run
if __name__ == "__main__":
    main()
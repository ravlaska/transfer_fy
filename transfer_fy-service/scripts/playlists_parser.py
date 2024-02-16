import argparse
import zipfile
import os
import json

# Loading playlist from json file
def playlist_loader(playlists_path):
    playlists_data = []
    # trying to list all the json playlist files and load them
    try:
        playlists = [os.path.join(playlists_path, f) for f in os.listdir(playlists_path) if os.path.isfile(os.path.join(playlists_path, f))]
        for idx, plist in enumerate(playlists):
            playlists_data.append([])

            # opening json
            with open(plist, encoding='utf-8') as pfile:
                tracklist = json.load(pfile)
            
            playlists_data[idx].append(tracklist['name']) # appending name of playlist

            # appending tracks URIs
            for track in tracklist['tracks']:
                playlists_data[idx].append(track['uri_track'])
    except:
        exit(1)
    
    return playlists_data

# Main function
def main():
    # parsing input arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("userId", help="User ID")
    parser.add_argument("filePath", help="Playlists file path")
    parser.add_argument("sessionId", help="ID of session")
    args = parser.parse_args()

    # defining variables
    file_path = f"uploads/{args.sessionId}/{args.filePath}"
    playlists_path = f"uploads/{args.sessionId}"

    # trying to extract zip with json playlists
    try:
        with zipfile.ZipFile(file_path, 'r') as playlists_archive:
            playlists_archive.extractall(playlists_path)
        if os.path.exists(file_path):
            os.remove(file_path)
    except:
        exit(1)
    
    playlists_data = playlist_loader(playlists_path)
    
    # printing playlists data to STDOUT for subprocess PIPE
    print(playlists_data)


# default run
if __name__ == "__main__":
    main()
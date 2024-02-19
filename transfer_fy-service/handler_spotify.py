from flask import render_template, send_file, session, request, redirect
import requests
import subprocess
import os
import shutil
import io
import ast

import configuration

# ========== Refreshing access token =========
def refresh_access_token():
    session['access_token'] = configuration.token_refresh(session['refresh_token'])

# ==================================== \/ EXPORT \/ ====================================

# ========= Spotify export playlists selection page =========
def playlist_export():
    # request playlists
    playlists = requests.get(f"https://api.spotify.com/v1/users/{session['user_id']}/playlists", headers={'Authorization': f"Bearer {session['access_token']}"})
    # if error -> refresh refresh access token
    if playlists != 200:
        refresh_access_token()
        playlists = requests.get(f"https://api.spotify.com/v1/users/{session['user_id']}/playlists", headers={'Authorization': f"Bearer {session['access_token']}"})

    return render_template('export.html', playlists=playlists.json())

# ========= Exporting selected playlists =========
def playlist_export_selection():
    selected_playlists_ids = request.form.getlist('playlist_ids')  # Get selected playlists
    if not selected_playlists_ids:
        return redirect('/error')
    
    # running script that exports playlists
    subprocess.run("source /venv/bin/activate", shell=True)
    subprocess.run(["/venv/bin/python3", "scripts/playlists_export.py", session['user_id'], session['session_id'], session['access_token'], str(selected_playlists_ids)])

    # rewriting file to memory
    return_file = io.BytesIO()
    with open(f"files/{session['session_id']}/playlists_{session['user_id']}.zip", 'rb') as fo:
        return_file.write(fo.read())
    return_file.seek(0)

    # cleaning data
    if os.path.exists(f"files/{session['session_id']}"):
        shutil.rmtree(f"files/{session['session_id']}")
    
    return send_file(return_file, mimetype='application/zip', download_name=f"playlists_{session['user_id']}.zip") # sending file to user


# ==================================== \/ IMPORT \/ ====================================

# ========= Spotify import file page =========
def playlist_import():
    if 'refresh_token' in session:
        return render_template('import.html')
    else:
        return redirect('/error')

# ========= Imported file handling =========
def playlist_import_selection():
    if 'file' not in request.files:
        return redirect('/error')
    
    file = request.files['file']
    
    # If the user does not select a file, the browser submits an empty file without a filename
    if file.filename == '':
        return redirect('/error')
    
    # If the file is present and has the correct extension
    if file and file.filename.endswith('.zip'):
        # directory handling
        upload_path = f"uploads/{session['session_id']}/" # defining output directory
        if not os.path.exists(upload_path):
            os.makedirs(upload_path)

        uploaded_file_name = 'playlists_[' + session['session_id'] + '].zip'

        # Save the file to the specified folder
        file.save(os.path.join(upload_path, uploaded_file_name))

        # running script that is parsing playlists
        subprocess.run("source /venv/bin/activate", shell=True)
        playparser = subprocess.run(["/venv/bin/python3", "scripts/playlists_parser.py", session['user_id'], uploaded_file_name, session['session_id']], stdout=subprocess.PIPE)

        # retrieving playlists data
        if playparser.returncode == 0:
            playlists_data = playparser.stdout.decode('utf-8')

        # creating variables for data
        playlists_titles = []
        playlists = []
        playlists_data = ast.literal_eval(playlists_data)

        # extracting data
        for item in playlists_data:
            playlists_titles.append(item[0])
            playlists.append(item[1:])

        return render_template('import_selected.html', playlists=playlists_titles)
    
    else:
        return redirect('/error')
    
def playlist_import_selected():
    selected_playlists_names = request.form.getlist('playlist_names')  # Get selected playlists

    # checking if any playlists were selected
    if not selected_playlists_names:
        return redirect('/error')
    
    # refreshing access_token
    refresh_access_token()

    # running script that imports playlists
    subprocess.run("source /venv/bin/activate", shell=True)
    subprocess.run(["/venv/bin/python3", "scripts/playlists_upload.py", session['user_id'], session['access_token'], session['session_id'], str(selected_playlists_names)])

    # cleaning data
    if os.path.exists(f"uploads/{session['session_id']}"):
        shutil.rmtree(f"uploads/{session['session_id']}")

    return render_template('success.html')

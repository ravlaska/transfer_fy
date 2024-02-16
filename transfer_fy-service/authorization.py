from flask import render_template, session, request, redirect
from urllib.parse import quote
import string
import random
import shutil
import os
import time

import configuration as configuration

configuration.params_load() # loading spotify API app parameters

# ========= Spotify login page =========
def login():
    # session handling
    state = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    session['spotify_auth_state'] = state
    scope = 'user-read-private user-read-email playlist-modify-public playlist-modify-private'

    # redirection to spotify authorization page
    return redirect('https://accounts.spotify.com/authorize?' +
                    'response_type=code' +
                    '&client_id=' + configuration.client_id +
                    '&scope=' + scope +
                    '&redirect_uri=' + quote(configuration.redirect_uri) +
                    '&state=' + state)

# ========= Logout - clear session ==========
def logout():
    cleaner() # cleaning old files
    session.clear() # cleaning session
    return redirect('/')

# ========= Cleaner ==========
def cleaner():
    # listing folders that are older than 40 mins and removing them
    for folder in os.listdir('uploads'):
        folder_path = os.path.join('uploads', folder)
        if os.path.isdir(folder_path) and os.path.getmtime(folder_path) < time.time() - 2400:
            shutil.rmtree(folder_path) # removing folder
    
    # removing dirs for current session ID
    if os.path.exists(f"uploads/{session['session_id']}"):
        shutil.rmtree(f"uploads/{session['session_id']}")

# ========= Retrieving spotify API code -> access token (callback from login page) =========
def callback():
    # extracting and validating state
    state = request.args.get('state', '')
    if state != session.get('spotify_auth_state', ''):
        return render_template('error.html')

    # extracting returned code
    session['code'] = request.args.get('code', '')
    # requesting for access token
    session['access_token'], session['refresh_token'] = configuration.get_tokens(session['code'])
    # extracting user ID
    session['user_id'] = configuration.get_user_id(session['access_token'])

    # requesting for tokens
    if session['access_token'] != False:
        return render_template('authorized.html')
    else:
        return render_template('error.html')

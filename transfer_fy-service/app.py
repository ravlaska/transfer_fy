from flask import Flask, render_template, session
import os
import uuid
import binascii

import authorization
import handler_spotify

# ========== USER SESSION HANDLER ==========
def session_handler():
    # Check if session_id exists in session
    if 'session_id' in session:
        session_id = session['session_id']
    else:
        # Generate a unique identifier for the user
        session_id = str(uuid.uuid4())
        # Store session_id in session
        session['session_id'] = session_id

# ========== APP CREATION ==========
app = Flask(__name__) # creating Flask app
app.secret_key = binascii.hexlify(os.urandom(24)).decode() # generating random secret key

# ============================================================ \/ URL ROUTES \/ ============================================================

# ========== HOME WEBPAGE ==========
@app.route('/')
def index():
    session_handler() # handling the session
    authorization.cleaner() # cleaning uploads files

    # user session handler
    if 'refresh_token' in session:
        return render_template('authorized.html') # printing unauthorized homepage
    else:
        return render_template('unauthorized.html') # printing authorized homepage

# ========== SPOTIFY ==========
app.add_url_rule('/login', view_func=authorization.login) # spotify login page
app.add_url_rule('/logout', view_func=authorization.logout) # logout
app.add_url_rule('/callback', view_func=authorization.callback) # spotify callback with tokens
app.add_url_rule('/export', view_func=handler_spotify.playlist_export) # spotify playlist export
app.add_url_rule('/export_selection', methods=['POST'], view_func=handler_spotify.playlist_export_selection) # spotify playlist export selection
app.add_url_rule('/import', view_func=handler_spotify.playlist_import) # spotify playlist import
app.add_url_rule('/import_selection', methods=['POST'], view_func=handler_spotify.playlist_import_selection) # spotify playlist import selection
app.add_url_rule('/import_selected_playlists', methods=['POST'], view_func=handler_spotify.playlist_import_selected) # selecting playlists to import

# ========== ERRORS ==========
# @app.errorhandler(Exception)
# def handle_error(error):
#     return render_template('error.html')

# ==============================
if __name__ == '__main__':
    app.run()

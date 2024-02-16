import base64
import requests
import json

# ========= Loading params =========
def params_load():
    global client_id
    global client_secret
    global redirect_uri

    # loading parameters
    with open('configs/params') as fparams:
        params = json.loads(fparams.read())

    # loading proper values
    client_id = params['client_id']
    client_secret = params['client_secret']
    redirect_uri = params['redirect_uri']

# ========= Retrieving [access_token] =========
def get_tokens(code):
    # creating request parameters
    headers = {
        'Authorization': 'Basic ' + base64.b64encode(f"{client_id}:{client_secret}".encode()).decode(),
        'Content-Type': 'application/x-www-form-urlencoded'
        }
    payload = {
        'code': code,
        'redirect_uri': redirect_uri,
        'grant_type': 'authorization_code'
    }
    # request call for access token and refresh token
    req_token = requests.post('https://accounts.spotify.com/api/token', headers=headers, data=payload)

    # if requesting for authorization ok
    if req_token.status_code == 200:
        response_token = req_token.json()
        access_token = response_token['access_token']
        refresh_token = response_token['refresh_token']

        return access_token, refresh_token
    else:
        return False
    
# ========= Determining ID of current user =========
def get_user_id(access_token):
    # request call
    req_user_id = requests.get('https://api.spotify.com/v1/me', headers={'Authorization': f'Bearer {access_token}'})

    # returning extracted user ID
    return req_user_id.json()['id']

# ========= Refreshing access token ==========
def token_refresh(refresh_token):
    # creating request parameters
    refresh_url = 'https://accounts.spotify.com/api/token'
    credentials = f"{client_id}:{client_secret}"
    auth_header = base64.b64encode(credentials.encode()).decode()
    headers = {
        'Authorization': 'Basic ' + auth_header,
        'Content-Type': 'application/x-www-form-urlencoded'
        }
    payload = {
        'refresh_token': refresh_token,
        'grant_type': 'refresh_token'
    }

    # making a 'token refresh' request
    req_refresh = requests.post(refresh_url, headers=headers, data=payload) # request token refresh
    refreshed_access_token = req_refresh.json()['access_token']

    return refreshed_access_token
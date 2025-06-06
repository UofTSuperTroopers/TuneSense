import requests
from flask import Flask, request, redirect, session, url_for
import os
from dotenv import load_dotenv
import os
import base64
import hashlib
import secrets
import requests
from flask import Flask, request, redirect

app = Flask(__name__)

CLIENT_ID = os.environ.get('SPOTIFY_API_KEY')
CLIENT_SECRET = os.environ.get('SPOTIFY_API_SECRET')

REDIRECT_URI = r'http://localhost:5000/callback'

SCOPE = 'user-read-private user-read-email'
AUTH_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL = 'https://accounts.spotify.com/api/token'

# Step 1: Generate PKCE code_verifier and code_challenge
code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(64)).rstrip(b'=').decode('utf-8')
code_challenge = base64.urlsafe_b64encode(
    hashlib.sha256(code_verifier.encode('utf-8')).digest()
).rstrip(b'=').decode('utf-8')

@app.route('/')
def login():
    params = {
        'client_id': CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': REDIRECT_URI,
        'code_challenge_method': 'S256',
        'code_challenge': code_challenge,
        'scope': SCOPE
    }
    auth_url = f"https://accounts.spotify.com/authorize?" + "&".join(f"{k}={v}" for k, v in params.items())
    return redirect(auth_url)


@app.route('/callback')
def callback():
    auth_code = request.args.get('code')

    # Step 4: Exchange code for token
    response = requests.post('https://accounts.spotify.com/api/token', data={
        'grant_type': 'authorization_code',
        'code': auth_code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'code_verifier': code_verifier
    })

    if response.ok:
        tokens = response.json()
        return f"Access Token: {tokens['access_token']}<br>Refresh Token: {tokens.get('refresh_token')}"
    else:
        return f"Error: {response.text}"

if __name__ == '__main__':
    app.run(port=5000, debug=True)
import base64
import hashlib
import secrets
import webbrowser
import os
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

from dotenv import load_dotenv
load_dotenv()

# Configuration
CLIENT_ID = os.environ.get('SPOTIFY_API_KEY')
CLIENT_SECRET = os.environ.get('SPOTIFY_API_SECRET')
# REDIRECT_URI = 'http://127.0.0.1:8888/callback'
REDIRECT_URI = 'https://tunesense-9f13a76c4fd9.herokuapp.com/callback'
SCOPE = 'user-read-private user-read-email'

# PKCE helper
def generate_pkce_pair():
    code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(64)).rstrip(b'=').decode()
    hashed = hashlib.sha256(code_verifier.encode()).digest()
    code_challenge = base64.urlsafe_b64encode(hashed).rstrip(b'=').decode()
    return code_verifier, code_challenge

# Simple handler to catch the redirect
class RedirectHandler(BaseHTTPRequestHandler):
    auth_code = None

    def do_GET(self):
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)
        if 'code' in query:
            RedirectHandler.auth_code = query['code'][0]
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"<h1>Auth complete. You can close this tab.</h1>")
        else:
            self.send_response(400)
            self.end_headers()

# Main PKCE flow
def authenticate():
    code_verifier, code_challenge = generate_pkce_pair()

    # Step 1: Launch auth request
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPE,
        "code_challenge_method": "S256",
        "code_challenge": code_challenge
    }
    auth_url = "https://accounts.spotify.com/authorize?" + "&".join(f"{k}={v}" for k, v in params.items())
    print("Opening browser for Spotify authentication...")
    webbrowser.open(auth_url)

    # Step 2: Start local server to catch redirect
    server = HTTPServer(('localhost', 8888), RedirectHandler)
    print("Waiting for redirect and auth code...")
    server.handle_request()  # One-shot

    if RedirectHandler.auth_code is None:
        print("Failed to get auth code.")
        return

    print(f"Received auth code: {RedirectHandler.auth_code}")

    # Step 3: Exchange for tokens
    token_response = requests.post("https://accounts.spotify.com/api/token", data={
        "grant_type": "authorization_code",
        "code": RedirectHandler.auth_code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "code_verifier": code_verifier
    })

    if token_response.ok:
        tokens = token_response.json()
        print(f"\n✅ Access Token: {tokens['access_token']}")
        if 'refresh_token' in tokens:
            print(f"🔄 Refresh Token: {tokens['refresh_token']}")
    else:
        print(f"❌ Token exchange failed: {token_response.text}")
    return tokens
  

if __name__ == "__main__":
    authenticate()
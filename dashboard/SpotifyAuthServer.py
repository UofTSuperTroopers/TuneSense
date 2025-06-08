# spotify_qt6_dashboard.py
import sys
import threading
import webbrowser
import json
import time
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QListWidget, QListWidgetItem
from PyQt6.QtCore import Qt, pyqtSignal
import requests

# Constants from your Spotify app
CLIENT_ID = '066f825dfe534df595c8bdb752b90845'
CLIENT_SECRET = 'c9be01e45c5e4d1ab3533a67f1d4f419'
REDIRECT_URI = 'http://127.0.0.1:8080/callback'
SCOPE = 'user-top-read user-read-recently-played user-library-read'
AUTH_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL = 'https://accounts.spotify.com/api/token'
API_BASE = 'https://api.spotify.com/v1'
TOKEN_FILE = 'spotify_token.json'

class SpotifyAuthServer(BaseHTTPRequestHandler):
    auth_code = None

    def do_GET(self):
        if self.path.startswith('/callback?code='):
            query = self.path.split('?')[1]
            params = dict(q.split('=') for q in query.split('&'))
            SpotifyAuthServer.auth_code = params.get('code')
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'Login successful. You can close this window.')

    @staticmethod
    def wait_for_code():
        httpd = HTTPServer(('localhost', 8080), SpotifyAuthServer)
        while not SpotifyAuthServer.auth_code:
            httpd.handle_request()
        httpd.server_close()
        return SpotifyAuthServer.auth_code

class SpotifyAPI:
    def __init__(self):
        self.access_token = None
        self.refresh_token = None
        self.load_tokens()

    def load_tokens(self):
        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, 'r') as f:
                tokens = json.load(f)
                self.access_token = tokens['access_token']
                self.refresh_token = tokens['refresh_token']

    def save_tokens(self):
        with open(TOKEN_FILE, 'w') as f:
            json.dump({
                'access_token': self.access_token,
                'refresh_token': self.refresh_token
            }, f)

    def get_auth_url(self):
        from urllib.parse import urlencode
        params = {
            'client_id': CLIENT_ID,
            'response_type': 'code',
            'redirect_uri': REDIRECT_URI,
            'scope': SCOPE
        }
        return f"{AUTH_URL}?{urlencode(params)}"

    def request_tokens(self, code):
        res = requests.post(TOKEN_URL, data={
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': REDIRECT_URI,
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET
        })
        res.raise_for_status()
        tokens = res.json()
        self.access_token = tokens['access_token']
        self.refresh_token = tokens['refresh_token']
        self.save_tokens()

    def api_get(self, endpoint):
        headers = {'Authorization': f'Bearer {self.access_token}'}
        res = requests.get(f'{API_BASE}{endpoint}', headers=headers)
        if res.status_code == 401:
            print("Access token expired")
            return None
        res.raise_for_status()
        return res.json()

    def get_saved_tracks(self):
        return self.api_get('/me/tracks?limit=20')

class MainWindow(QMainWindow):
    profile_loaded = pyqtSignal(dict)  # This is your signal

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Spotify Dashboard")
        self.setGeometry(100, 100, 600, 400)

        self.api = SpotifyAPI()
        self.label = QLabel("Not logged in", alignment=Qt.AlignmentFlag.AlignCenter)
        self.login_button = QPushButton("Login to Spotify")
        self.login_button.clicked.connect(self.login)

        self.track_list = QListWidget()
        self.track_list.setVisible(False)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.login_button)
        layout.addWidget(self.track_list)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Connect the signal to the handler method (different name!)
        self.profile_loaded.connect(self.on_profile_loaded)

    def login(self):
        url = self.api.get_auth_url()
        webbrowser.open(url)

        def run_auth_flow():
            code = SpotifyAuthServer.wait_for_code()
            self.api.request_tokens(code)
            profile = self.api.api_get('/me')
            if profile:
                self.profile_loaded.emit(profile)  # emit signal safely

        threading.Thread(target=run_auth_flow, daemon=True).start()

    # Renamed this method so it doesn't clash with the signal name
    def on_profile_loaded(self, profile):
        self.label.setText(f"Logged in as {profile['display_name']}")
        self.load_saved_tracks()

    def load_saved_tracks(self):
        data = self.api.get_saved_tracks()
        if data:
            self.track_list.setVisible(True)
            self.track_list.clear()
            for item in data['items']:
                track = item['track']
                name = track['name']
                artist = track['artists'][0]['name']
                display = f"{name} - {artist}"
                QListWidgetItem(display, self.track_list)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
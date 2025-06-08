import urllib.parse
import os
import threading
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler

from spotipy.oauth2 import SpotifyOAuth

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QApplication
from PyQt6.QtCore import QUrl, QTimer, pyqtSignal
from PyQt6.QtWebEngineWidgets import QWebEngineView

from dashboard.tunesense.windows.MainWindow import MainWindow

from dotenv import load_dotenv




load_dotenv()

CLIENT_ID = os.environ.get('SPOTIFY_API_KEY')
CLIENT_SECRET = os.environ.get('SPOTIFY_API_SECRET')
REDIRECT_URI = 'http://127.0.0.1:8888/callback'
SCOPE = 'user-read-recently-played user-read-playback-state user-top-read user-library-read user-read-private user-follow-read'


class LoginWindow(QWidget):
  login_successful = pyqtSignal(str)
  def __init__(self):
    super().__init__()
    self.setWindowTitle('TuneSense🎤')
    
    self.sp_oauth = SpotifyOAuth(client_id=CLIENT_ID,
                                 client_secret=CLIENT_SECRET,
                                 redirect_uri=REDIRECT_URI,
                                 scope=SCOPE
    )

    self.login_successful.connect(self.open_main)

    self.login_button = QPushButton('Login to Spotify.')
    layout = QVBoxLayout()
    layout.addWidget(QLabel("Welcome to TuneSense"))
    layout.addWidget(self.login_button)
    self.setLayout(layout)

    self.login_button.clicked.connect(self.start_login)
  
  def start_login(self):
    threading.Thread(target=self.start_http_server, daemon=True).start()
    auth_url = self.sp_oauth.get_authorize_url()
    webbrowser.open(auth_url)


    # self.web = QWebEngineView()
    # self.web.load(QUrl(auth_url))
    # self.web.urlChanged.connect(self.on_url_changed)

  def start_http_server(self):
    parent = self

    class OAuthCallbackHandler(BaseHTTPRequestHandler):
      def do_GET(self_2):
        parsed = urllib.parse.urlparse(self_2.path)
        params = urllib.parse.parse_qs(parsed.query)
        print(f'params = {params}')
        if 'code' in params:
          code = params['code'][0]
          token_info = parent.sp_oauth.get_access_token(code)
          print(f'[DEBUG]: token_info = {token_info}')
          print(f'[DEBUG]: token_info["expires_at"] = {token_info.get("expires_at")}')
          parent.access_token = token_info['access_token']
          print(f'[LOGGER]: access_token = {parent.access_token}')

          parent.login_successful.emit(parent.access_token)
          # self.open_main()

          self_2.send_response(200)
          self_2.send_header('Content-type', 'text/html')
          self_2.end_headers()
          self_2.wfile.write(b'<b>Login successful. Close to proceed to TuneSense</b>')
        else:
          self_2.send_response(400)
          self_2.end_headers()

    server = HTTPServer(('127.0.0.1', 8888), OAuthCallbackHandler)
    server.serve_forever()
    
  def on_url_changed(self, url):
    if url.toString().startswith(REDIRECT_URI):
      query = urllib.parse.urlparse(url.toString()).query
      code = urllib.parse.parse_qs(query).get('code', [None])[0]
      if code:
        token_info = self.sp_oauth.get_access_token(code)
        self.access_token = token_info['access_token']
        QTimer.singleShot(0, self.open_main)

  def open_main(self, access_token):
    self.hide()
    self.main_window = MainWindow(access_token)
    self.main_window.show()

  
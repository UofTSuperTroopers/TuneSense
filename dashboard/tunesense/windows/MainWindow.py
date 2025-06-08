from PyQt6.QtWidgets import QMainWindow, QLabel, QListWidget, QListWidgetItem, QVBoxLayout, QWidget
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtCore import QUrl

from io import BytesIO
import spotipy
import requests

class MainWindow(QMainWindow):
  def __init__(self, access_token):
    super().__init__()
    self.setWindowTitle('SPOTIFY RECOMMENDATIONS')
    self.sp = spotipy.Spotify(auth=access_token)

    self.init_ui()
    self.load_recommendations()

  def init_ui(self):
    widget = QWidget()
    layout = QVBoxLayout()

    self.label = QLabel('Recommendations: ')
    self.list_widget = QListWidget()

    layout.addWidget(self.label)
    layout.addWidget(self.list_widget)


    self.media_player = QMediaPlayer()
    self.audio_output = QAudioOutput()

    self.media_player.setAudioOutput(self.audio_output)

    widget.setLayout(layout)
    self.setCentralWidget(widget)

  def load_recommendations(self):
    print('[LOGGER]: load_recommendations()')

    self.list_widget.clear()
    self.label.setText('Loading recommendations...')

    # Step 1: Try to fetch top tracks
    try:
        top_tracks = self.sp.current_user_top_tracks(limit=5, time_range='long_term')
        top_track_ids = [track['id'] for track in top_tracks.get('items', []) if track.get('id')]
    except Exception as e:
        print(f'[ERROR]: Failed to fetch top tracks: {e}')
        top_track_ids = []

    # Step 2: Determine seed source
    recs = None
    if top_track_ids:
        print(f'[LOGGER]: Using top tracks as seeds: {top_track_ids[:2]}')
        try:
            recs = self.sp.recommendations(seed_tracks=top_track_ids[:2], limit=10)
        except Exception as e:
            print(f'[ERROR]: Failed to get recommendations with top tracks: {e}')
    if not recs or not recs.get('tracks'):
        print('[WARN]: Falling back to seed genres.')
        try:
            recs = self.sp.recommendations(seed_genres=['pop', 'rock'], limit=10)
        except Exception as e:
            print(f'[ERROR]: Failed to get recommendations with genres: {e}')
            self.label.setText('Failed to load recommendations.')
            return

    # Step 3: Populate the list widget
    tracks = recs.get('tracks', [])
    if not tracks:
        print('[ERROR]: Spotify returned no recommendations.')
        self.label.setText('No recommendations available.')
        return

    for track in tracks:
        name = track.get('name')
        artist = track['artists'][0]['name'] if track.get('artists') else 'Unknown Artist'
        preview_url = track.get('preview_url')
        album_images = track.get('album', {}).get('images', [])
        album_url = next((img['url'] for img in album_images if img), None)

        if not preview_url:
            continue  # skip non-previewable tracks

        item = QListWidgetItem(f'{name} - {artist}')
        if album_url:
            try:
                image_data = requests.get(album_url, timeout=5).content
                pixmap = QPixmap()
                pixmap.loadFromData(image_data)
                item.setIcon(QIcon(pixmap))
            except Exception as e:
                print(f'[WARN]: Failed to load album art for {name}: {e}')

        item.setData(1000, preview_url)
        self.list_widget.addItem(item)

    self.label.setText('Recommendations loaded.')
    self.list_widget.itemClicked.connect(self.play_preview)


  def play_preview(self, item):
    url = item.data(1000)
    if url:
      self.media_player.setSource(QUrl(url))
      self.media_player.play()
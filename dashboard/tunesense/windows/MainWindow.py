from PyQt6.QtWidgets import QMainWindow, QLabel, QListWidget, QListWidgetItem, QVBoxLayout, QWidget
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtCore import QUrl

import requests

class MainWindow(QMainWindow):
    def __init__(self, access_token):
        super().__init__()
        self.setWindowTitle('SPOTIFY RECOMMENDATIONS')
        self.access_token = access_token

        self.init_ui()
        self.load_recommendations()

    def init_ui(self):
        widget = QWidget()
        layout = QVBoxLayout()

        self.label = QLabel('Loading recommendations...')
        self.list_widget = QListWidget()

        layout.addWidget(self.label)
        layout.addWidget(self.list_widget)

        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)

        widget.setLayout(layout)
        self.setCentralWidget(widget)

        self.list_widget.itemClicked.connect(self.play_preview)

    def load_recommendations(self):
        print('[LOGGER]: load_recommendations()')

        headers = {
            'Authorization': f'Bearer {self.access_token}'
        }

        # Step 1: Get user's top tracks (limit 5)
        top_tracks_url = 'https://api.spotify.com/v1/me/top/tracks?limit=5&time_range=long_term'
        response = requests.get(top_tracks_url, headers=headers)

        if response.status_code != 200:
            print(f'[ERROR]: Failed to fetch top tracks: {response.status_code} {response.text}')
            self.label.setText('Failed to fetch top tracks.')
            return

        data = response.json()
        top_tracks = data.get('items', [])
        seed_track_ids = [track['id'] for track in top_tracks if 'id' in track and track['id']]
        print(f'[DEBUG]: seed_track_ids = {seed_track_ids}')

        # Step 2: Build recommendations request
        recs_url = 'https://api.spotify.com/v1/recommendations'
        params = {'limit': 10}

        if seed_track_ids:
            params['seed_tracks'] = ','.join(seed_track_ids[:2])
            print(f'[LOGGER]: Using top tracks as seeds: {params["seed_tracks"]}')
        else:
            # Fetch valid genres from Spotify
            genres_url = 'https://api.spotify.com/v1/recommendations/available-genre-seeds'
            genres_resp = requests.get(genres_url, headers=headers)
            if genres_resp.status_code == 200:
                genres = genres_resp.json().get('genres', [])
                print(f'[DEBUG]: Available genres: {genres}')
                if genres:
                    params['seed_genres'] = ','.join(genres[:2])
                    print(f'[LOGGER]: Using fallback genres: {params["seed_genres"]}')
                else:
                    print('[ERROR]: No available genres found.')
                    self.label.setText('No available genres found for recommendations.')
                    return
            else:
                print(f'[ERROR]: Failed to fetch available genres: {genres_resp.status_code} {genres_resp.text}')
                self.label.setText('Failed to fetch available genres.')
                return

        print(f'[DEBUG]: Recommendations request params: {params}')
        recs_response = requests.get(recs_url, headers=headers, params=params)

        if recs_response.status_code != 200:
            print(f'[ERROR]: Failed to fetch recommendations: {recs_response.status_code} {recs_response.text}')
            self.label.setText(f'Failed to fetch recommendations: {recs_response.text}')
            return

        recs_data = recs_response.json()
        tracks = recs_data.get('tracks', [])

        if not tracks:
            self.label.setText('No recommendations found.')
            return

        self.list_widget.clear()

        for track in tracks:
            name = track.get('name', 'Unknown Track')
            artist = track.get('artists', [{}])[0].get('name', 'Unknown Artist')
            preview_url = track.get('preview_url')
            album_images = track.get('album', {}).get('images', [])

            # Pick the medium size image if available
            album_url = None
            if len(album_images) >= 2:
                album_url = album_images[1]['url']
            elif len(album_images) == 1:
                album_url = album_images[0]['url']

            if not preview_url:
                continue  # skip tracks without previews

            item_text = f"{name} - {artist}"
            item = QListWidgetItem(item_text)

            if album_url:
                try:
                    image_resp = requests.get(album_url, timeout=5)
                    image_resp.raise_for_status()
                    pixmap = QPixmap()
                    pixmap.loadFromData(image_resp.content)
                    item.setIcon(QIcon(pixmap))
                except Exception as e:
                    print(f'[WARN]: Failed to load album image for "{name}": {e}')

            item.setData(1000, preview_url)
            self.list_widget.addItem(item)

        self.label.setText('Recommendations loaded.')

    def play_preview(self, item):
        url = item.data(1000)
        if url:
            print(f'[LOGGER]: Playing preview: {url}')
            self.media_player.setSource(QUrl(url))
            self.media_player.play()
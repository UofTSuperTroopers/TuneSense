import sys
import os
import tempfile
import time

import numpy as np
import pandas as pd
import joblib
import librosa
from librosa.feature.rhythm import tempo
import yt_dlp

import matplotlib.pyplot as plt

from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtWidgets import QApplication, QMainWindow, QLineEdit, QPushButton, QListWidget, QListWidgetItem, QVBoxLayout, QWidget, QHBoxLayout
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtCore import QUrl, Qt, QThread, pyqtSignal

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from googleapiclient.discovery import build
import isodate

YOUTUBE_API_KEY = 'AIzaSyB9KiBv0NJ-6NJGOibjELw0MN-RMcIL2vs'

def yt_api_search(query, max_results=5):
  youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

  search_response = youtube.search().list(
    part="snippet",
    q=query,
    type="video",
    maxResults=max_results
  ).execute()

  video_ids = [item['id']['videoId'] for item in search_response['items']]

  videos_response = youtube.videos().list(
      part="snippet,contentDetails",
      id=",".join(video_ids)
  ).execute()

  results = []
  for item in videos_response['items']:
    video_id = item['id']
    title = item['snippet']['title']
    duration = item['contentDetails']['duration']
    duration_sec = int(isodate.parse_duration(duration).total_seconds())
    results.append({
      'title': title,
      'url': f"https://www.youtube.com/watch?v={video_id}",
      'duration': duration_sec
    })

  return results

class YouTubeDownloader(QThread):
    download_done = pyqtSignal(str)

    def __init__(self, url):
        super().__init__()
        self.url = url

    def run(self):
        try:
            out_path = os.path.join(tempfile.gettempdir(), f'video_{int(time.time())}.%(ext)s')
            ydl_opts = {
                'format': 'bestvideo+bestaudio/best',
                'merge_output_format': 'mp4',
                'outtmpl': out_path,
                'quiet': True,
            }
            print(f"Downloading video from {self.url} to {out_path}")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.url, download=True)
                video_path = ydl.prepare_filename(info)
                if not video_path.endswith('.mp4'):
                    video_path = os.path.splitext(video_path)[0] + '.mp4'
            self.download_done.emit(video_path)
        except Exception as e:
            self.download_done.emit(f"ERROR::{e}")


class FeatureExtractor(QThread):
    result_ready = pyqtSignal(dict)

    def __init__(self, audio_path):
        super().__init__()
        self.audio_path = audio_path
        self.model = joblib.load("multi_audio_model.pkl")

    def run(self):
        try:
            y, sr = librosa.load(self.audio_path, sr=22050)
            mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)  # 13 MFCCs is typical
            mfcc_means = np.mean(mfcc, axis=1)

            features = {
                'chroma_stft': np.mean(librosa.feature.chroma_stft(y=y, sr=sr)),
                'rmse': np.mean(librosa.feature.rms(y=y)),
                'spectral_centroid': np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)),
                'spectral_bandwidth': np.mean(librosa.feature.spectral_bandwidth(y=y, sr=sr)),
                'rolloff': np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr)),
                'zero_crossing_rate': np.mean(librosa.feature.zero_crossing_rate(y=y)),
                'tempo': tempo(y=y, sr=sr)[0],
            }
            for i, mfcc_feature in enumerate(mfcc_means, start=1):
                features[f'mfcc{i}'] = mfcc_feature
            
            df = pd.DataFrame([features])
            prediction = self.model.predict(df)[0]
            result = {k: v for k, v in zip(['danceability', 'energy', 'valence'], prediction)}
            self.result_ready.emit(result)
        except Exception as e:
            print(f"Feature extraction error: {e}")


class RadarChart(QWidget):
    def __init__(self):
        super().__init__()
        self.figure, self.ax = plt.subplots(subplot_kw={'projection': 'polar'})
        self.canvas = FigureCanvas(self.figure)
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def update_plot(self, data):
        self.ax.clear()

        labels = list(data.keys())
        values = list(data.values())

        values += values[:1]

        angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
        angles += angles[:1]

        self.ax.plot(angles, values, 'o-', linewidth=2)
        self.ax.fill(angles, values, alpha=0.25)
        
        for size, alpha in [(18, 0.1), (15, 0.2), (12, 0.3)]:
            self.ax.plot(angles, values, 'o', markersize=size, color='#ffd700', alpha=alpha)

        self.ax.set_xticks(angles[:-1])
        self.ax.set_xticklabels(labels)
        self.ax.grid(False)
        self.ax.spines['polar'].set_visible(False)
        self.canvas.draw()


class SongPredictorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TuneSense 🎶")
        self.setGeometry(200, 200, 1600, 1200)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search for a song...")

        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.perform_search)

        self.results_list = QListWidget()
        self.results_list.itemClicked.connect(self.play_selected_song)

        self.radar_chart = RadarChart()
        self.video_widget = QVideoWidget()

        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()

        self.media_player.mediaStatusChanged.connect(self.handle_media_status)

        self.media_player.setVideoOutput(self.video_widget)
        self.media_player.setAudioOutput(self.audio_output)

        self.video_widget.setMinimumHeight(400)
        self.video_widget.setMaximumWidth(600)
        layout = QVBoxLayout()
        top_row = QHBoxLayout()
        top_row.addWidget(self.search_bar)
        top_row.addWidget(self.search_button)

        layout.addLayout(top_row)

        layout.addWidget(self.results_list)
        layout.addWidget(self.video_widget)
        layout.addWidget(self.radar_chart)


        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def handle_media_status(self, status):
        if status == QMediaPlayer.MediaStatus.LoadedMedia:
            self.media_player.play()
        elif status == QMediaPlayer.MediaStatus.LoadingMedia:
            self.media_player.setSource(QUrl())
        elif status == QMediaPlayer.MediaStatus.InvalidMedia:
            self.results_list.addItem(QListWidgetItem("❌ Media error occurred."))

    def perform_search(self):
        query = self.search_bar.text().strip()
        self.results_list.clear()

        if not query:
            self.results_list.addItem(QListWidgetItem("❌ Please enter a search query."))
            return
        try:
            results = yt_api_search(query)
            if not results:
                self.results_list.addItem(QListWidgetItem("❌ No results found."))
                return
            
            for entry in results:
                mins = entry['duration'] // 60
                secs = entry['duration'] % 60
                item_text = f"{entry['title']} ({mins:02}:{secs:02})"
                item = QListWidgetItem(item_text)
                item.setData(Qt.ItemDataRole.UserRole, entry['url'])
                self.results_list.addItem(item)
        except Exception as e:
            self.results_list.addItem(QListWidgetItem(f"❌ Search failed: {e}"))

    def play_selected_song(self, item):
        url = item.data(Qt.ItemDataRole.UserRole)
        self.results_list.setDisabled(True)
        self.results_list.clear()
        self.results_list.addItem("Downloading...")

        self.downloader = YouTubeDownloader(url)
        self.downloader.download_done.connect(self.handle_download_result)
        self.downloader.start()

    def handle_download_result(self, path):
        self.results_list.clear()
        self.results_list.setDisabled(False)

        if path.startswith("ERROR::"):
            self.results_list.addItem(f"❌ Failed to download: {path[7:]}")
            return

        self.media_player.stop()
        self.media_player.setSource(QUrl())
        self.media_player.setSource(QUrl.fromLocalFile(path))
        self.media_player.play()

        self.worker = FeatureExtractor(path)
        self.worker.result_ready.connect(self.radar_chart.update_plot)
        self.worker.start()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SongPredictorApp()
    window.show()
    sys.exit(app.exec())

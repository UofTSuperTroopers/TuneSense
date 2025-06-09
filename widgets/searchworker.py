import sys
import requests
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QListWidget, QListWidgetItem, QMessageBox


import yt_dlp
from io import BytesIO

class SearchWorker(QThread):
    results_ready = pyqtSignal(list)

    def __init__(self, query):
        super().__init__()
        self.query = query

    def run(self):
        ydl_opts = {
            'quiet': True,
            'skip_download': True,
            'format': 'bestaudio/best',
            'default_search': 'ytsearch5',
            'nocheckcertificate': True,
        }
        try:
            ydl = yt_dlp.YoutubeDL(ydl_opts)
            info = ydl.extract_info(self.query, download=False)
            self.results_ready.emit(info.get('entries', []))
        except Exception as e:
            self.results_ready.emit([])

class YouTubeDownloader(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TuneSense 🎵🎶")
        self.setGeometry(300, 300, 600, 500)

        self.layout = QVBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search YouTube...")
        self.layout.addWidget(self.search_input)

        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.start_search)
        self.layout.addWidget(self.search_button)

        self.result_list = QListWidget()
        self.result_list.setIconSize(QPixmap(160, 90).size())
        self.result_list.itemDoubleClicked.connect(self.download_selected)
        self.layout.addWidget(self.result_list)

        self.quality_input = QLineEdit()
        self.quality_input.setPlaceholderText("Preferred MP3 quality (e.g., 192)")
        self.layout.addWidget(self.quality_input)

        self.setLayout(self.layout)
        self.videos = []

    def start_search(self):
        query = self.search_input.text().strip()
        if not query:
            QMessageBox.warning(self, "Error", "Please enter a search query.")
            return

        self.result_list.clear()
        self.search_button.setEnabled(False)

        self.worker = SearchWorker(query)
        self.worker.results_ready.connect(self.show_results)
        self.worker.start()

    def show_results(self, entries):
        self.videos = entries
        for video in entries:
            title = video.get('title', 'No title')
            duration = video.get('duration', 0)
            thumbnail_url = video.get('thumbnail')

            mins, secs = divmod(duration, 60)
            label = f"{title} [{mins}:{secs:02d}]"

            item = QListWidgetItem(label)

            # Attempt to fetch and attach thumbnail
            try:
                with requests.get(thumbnail_url, timeout=3, stream=True) as response:
                    response.raise_for_status()
                    thumb_data = BytesIO()
                    for chunk in response.iter_content(chunk_size=8192):
                        thumb_data.write(chunk)
                thumb_data.seek(0)
                pixmap = QPixmap()
                pixmap.loadFromData(thumb_data.read())
                icon = QIcon(pixmap.scaled(160, 90, Qt.AspectRatioMode.KeepAspectRatio))
                item.setIcon(icon)
            except Exception:
                pass  # fallback: no thumbnail

            self.result_list.addItem(item)

        self.search_button.setEnabled(True)

    def download_selected(self, item):
        idx = self.result_list.row(item)
        video = self.videos[idx]
        url = video.get('webpage_url')
        title = video.get('title', 'video')

        reply = QMessageBox.question(
            self,
            "Download",
            f"Download MP3 for:\n{title}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.download_audio(url, title)
    def download_audio(self, url, title):
        ydl_opts = {
            'format': 'bestaudio/best',
            'skip_download': True,
            'default_search': 'ytsearch3',
            'nocheckcertificate': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'outtmpl': f"{title}.%(ext)s",
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': self.quality_input.text().strip() or '192',
            }],
        }
        try:
            ydl = yt_dlp.YoutubeDL(ydl_opts)
            ydl.download([url])
            QMessageBox.information(self, "Success", f"Downloaded: {title}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Download failed:\n{e}")
            QMessageBox.critical(self, "Error", f"Download failed:\n{e}")



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = YouTubeDownloader()
    window.show()
    sys.exit(app.exec())
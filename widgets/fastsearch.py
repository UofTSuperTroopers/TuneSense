import sys
import threading
import requests
from io import BytesIO

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLineEdit, QPushButton,
    QListWidget, QListWidgetItem, QVBoxLayout, QWidget
)
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import QTimer
from yt_dlp import YoutubeDL


class YouTubeSearchApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YouTube Search")
        self.setGeometry(100, 100, 700, 500)

        # UI Elements
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search YouTube...")
        self.search_button = QPushButton("Search")
        self.results_list = QListWidget()

        layout = QVBoxLayout()
        layout.addWidget(self.search_input)
        layout.addWidget(self.search_button)
        layout.addWidget(self.results_list)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Connect button
        self.search_button.clicked.connect(self.start_search)

    def start_search(self):
        query = self.search_input.text().strip()
        if not query:
            return
        self.search_button.setEnabled(False)
        self.results_list.clear()
        threading.Thread(target=self.run_search, args=(query,), daemon=True).start()

    def run_search(self, query):
        ydl_opts = {
            "quiet": True,
            "skip_download": True,
            "extract_flat": True,
            "force_generic_extractor": True,
            "default_search": "ytsearch5",
        }

        try:
            with YoutubeDL(ydl_opts) as ydl:
                result = ydl.extract_info(query, download=False)
                entries = result.get("entries", [])
                for entry in entries:
                    title = entry.get("title", "No title")
                    video_id = entry.get("id")
                    thumb = f'https://i.ytimg.com/vi/{video_id}/hqdefault.jpg' if video_id else None
                    video_url = entry.get('url')
                    if not video_url.startswith('http'):
                        video_url = f'https://www.youtube.com/watch?v={video_url}'
                    self.add_result(title, thumb, video_url)
        except Exception as e:
            print(f"Search failed: {e}")
        finally:
            QTimer.singleShot(0, lambda: self.search_button.setEnabled(True))

    def add_result(self, title, thumbnail_url, video_url):
        def fetch_and_add():
            icon = QIcon()
            if thumbnail_url:
                try:
                    response = requests.get(thumbnail_url, timeout=5)
                    pixmap = QPixmap()
                    pixmap.loadFromData(response.content)
                    icon = QIcon(pixmap)
                except Exception as e:
                    print(f"Thumbnail fetch failed: {e}")

            def update_ui():
                item = QListWidgetItem(icon, title)
                item.setToolTip(video_url)
                self.results_list.addItem(item)

            QTimer.singleShot(0, update_ui)

        threading.Thread(target=fetch_and_add, daemon=True).start()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = YouTubeSearchApp()
    window.show()
    sys.exit(app.exec())
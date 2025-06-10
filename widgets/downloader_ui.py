from PyQt6.QtCore import Qt, QSize, QThreadPool
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QPushButton,
    QListWidget, QListWidgetItem, QMessageBox, QLabel
)
from widgets.searchworker import SearchWorker
from widgets.thumbnailthread import (
    get_audio_features,
    get_recommendations,
    fetch_metadata,
    RadarChartCanvas, ThumbnailSignalEmitter, ThumbnailWorker
)

class YouTubeDownloader(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TuneSense 🎵🎶")
        self.setGeometry(300, 300, 800, 600)

        self.layout = QVBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search YouTube...")
        self.layout.addWidget(self.search_input)

        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.start_search)
        self.layout.addWidget(self.search_button)

        self.result_list = QListWidget()
        self.result_list.setIconSize(QSize(160, 90))
        self.result_list.itemClicked.connect(self.show_recommendations_and_chart)
        self.layout.addWidget(self.result_list)

        self.quality_input = QLineEdit()
        self.quality_input.setPlaceholderText("Preferred MP3 quality (e.g., 192)")
        self.layout.addWidget(self.quality_input)

        self.recommend_label = QLabel("🎧 Recommendations:")
        self.layout.addWidget(self.recommend_label)
        self.recommend_list = QListWidget()
        self.layout.addWidget(self.recommend_list)

        self.chart_placeholder = QLabel("📊 Radar Chart:")
        self.layout.addWidget(self.chart_placeholder)

        self.setLayout(self.layout)

        self.threadpool = QThreadPool()
        self.thumbnail_emitter = ThumbnailSignalEmitter()
        self.thumbnail_emitter.signal.connect(self.set_thumbnail)
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
        self.result_list.clear()

        for video in entries:
            title = video.get('title', 'No title')
            duration = video.get('duration', 0)
            thumbnail_url = video.get('thumbnails', [{}])[0].get('url')
            track_id = video.get('id')  # use video ID as track_id

            mins, secs = divmod(int(duration or 0), 60)
            label = f"{title} [{mins}:{secs:02d}]"

            item = QListWidgetItem(label)
            item.setData(Qt.ItemDataRole.UserRole, title)

            if thumbnail_url:
                worker = ThumbnailWorker(thumbnail_url, item, self.thumbnail_emitter.signal)
                self.threadpool.start(worker)

            self.result_list.addItem(item)

        self.search_button.setEnabled(True)

    def set_thumbnail(self, item, icon):
        item.setIcon(icon)
        self.result_list.repaint()

    def show_recommendations_and_chart(self, item):
        title = item.data(Qt.ItemDataRole.UserRole)
        features = get_audio_features(None, title=title)

        if not features:
            QMessageBox.warning(self, "Missing", "No features found for this song.")
            return

        rec_vectors = get_recommendations(features)
        rec_data = fetch_metadata(rec_vectors)

        self.recommend_list.clear()
        for song in rec_data:
            self.recommend_list.addItem(QListWidgetItem(song.get('title', song.get('track_id', 'Unknown'))))

        radar = RadarChartCanvas(features, self)
        self.layout.replaceWidget(self.chart_placeholder, radar)
        self.chart_placeholder.hide()
        radar.show()

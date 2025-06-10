from PyQt6.QtWidgets import QApplication
import sys

from widgets.downloader_ui import YouTubeDownloader

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = YouTubeDownloader()
    window.show()
    sys.exit(app.exec())

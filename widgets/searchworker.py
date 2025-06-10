from PyQt6.QtCore import QThread, pyqtSignal
import yt_dlp

class SearchWorker(QThread):
    results_ready = pyqtSignal(list)

    def __init__(self, query):
        super().__init__()
        self.query = query

    def run(self):
        ydl_opts = {
            'quiet': False,
            'skip_download': True,
            'extract_flat': True,  # ⬅️ Keep this False to retain full metadata
            # 'format': 'bestaudio/best',
            'default_search': 'ytsearch5',
            'nocheckcertificate': True,
            'force_generic_extractor': False,  # ⬅️ Let yt_dlp use YouTube’s own logic
            'simulate': True,  # ⬅️ Avoid triggering extra format extraction
            'forcejson': True,  # ⬅️ Just return metadata as JSON

        }
        try:
            print(f"🔍 Searching: ytsearch5:{self.query}")
            ydl = yt_dlp.YoutubeDL(ydl_opts)
            info = ydl.extract_info(f"ytsearch5:{self.query}", download=False)

            # Emit results (either a list or single item wrapped in a list)
            if 'entries' in info and isinstance(info['entries'], list):
                self.results_ready.emit(info['entries'])
            else:
                self.results_ready.emit([info])
        except Exception as e:
            print(f"❌ SearchWorker error: {e}")
            self.results_ready.emit([])
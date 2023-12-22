import os
from tasks import download_torrent_task, download_youtube_task, copy_local_video_task


class VideoDownloader:
    def __init__(self, url, video_id):
        self.url = url
        self.type = None
        self.video_id = video_id

    def parse(self):
        if os.path.isfile(self.url):
            if self.is_video_file():
                self.type = "Video"
            elif self.is_torrent_file():
                self.type = "Torrent"
        elif self.is_youtube_link():
            self.type = "YouTube"
        elif self.is_torrent_magnet():
            self.type = "Magnet"
        else:
            print("Unsupported URL format")
        return self

    def download(self, output_path="videos/"):
        if self.type is None:
            print("Type not determined. Run parse() first.")
        elif self.type == "YouTube":
            download_youtube_task.delay(self.url, output_path, self.video_id)
        elif self.type == "Video":
            copy_local_video_task.delay(self.url, output_path, self.video_id)
        elif self.type == "Magnet" or self.type == "Torrent":
            download_torrent_task.delay(self.url, output_path, self.video_id)
        else:
            print(f"Unsupported type: {self.type}")
        return self

    def is_video_file(self):
        video_extensions = ['.mp4', '.avi', '.mkv', '.mov', '.wmv']
        return any(self.url.lower().endswith(ext) for ext in video_extensions)

    def is_torrent_file(self):
        return self.url.lower().endswith('.torrent')

    def is_torrent_magnet(self):
        return self.url.lower().startswith('magnet:')

    def is_youtube_link(self):
        return any(url in self.url.lower() for url in ["youtube.com", "youtu.be"])

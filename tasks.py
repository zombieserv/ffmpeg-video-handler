import shutil
import subprocess
from pathlib import Path
from celery import Celery
from env import *
from pytube import YouTube
from torrentp import TorrentDownloader
from models import Video
from utils import find_video_file

app = Celery('python-ffmpeg-handler', broker='redis://redis:6379/0', include=['tasks'])


@app.task
def download_torrent_task(url, output_path, video_id):
    video = Video.objects.get(id=video_id)
    video.set_downloading()
    try:
        torrent_file = TorrentDownloader(url, output_path)
        torrent_file.start_download()


        # TODO: Improve this
        _torrent_name = torrent_file._downloader._torrent_info.name if torrent_file._downloader else 'unknown_name'
        _save_path = torrent_file._save_path
        _file_name = torrent_file._downloader._status.name
        _full_path = os.path.join(_save_path, _file_name)

        _path = Path(_full_path)
        video_file = _full_path if _path.is_file() else (find_video_file(_path) if _path.is_dir() and find_video_file
                                                         else None)
        remove_dir = None
        if _path.is_dir():
            remove_dir = _full_path

        video.set_name(_torrent_name)
        video.set_processing()

        handle_video_file.delay(video_file, video_id, remove_dir)
        return f"Torrent download completed. Files saved in {output_path}"
    except Exception as e:
        video.set_error()
        return f"Error: {e}"


@app.task
def download_youtube_task(url, output_path, video_id):
    video = Video.objects.get(id=video_id)
    video.set_downloading()
    try:
        yt = YouTube(url)
        video_stream = yt.streams.get_highest_resolution()
        handle_url = video_stream.download(output_path)
        video.set_name(yt.title)
        video.set_processing()
        handle_video_file.delay(handle_url, video_id)
        return f"Youtube download completed. Files saved in {handle_url}"
    except Exception as e:
        video.set_error()
        return f"Error: {e}"


@app.task
def copy_local_video_task(url, output_path, video_id):
    video = Video.objects.get(id=video_id)
    try:
        os.makedirs(output_path, exist_ok=True)
        file_name = os.path.basename(url)
        target_path = os.path.join(output_path, file_name)
        shutil.copy2(url, target_path)
        file_name_without_extension = os.path.splitext(file_name)[0]
        video.set_name(file_name_without_extension)
        video.set_processing()
        handle_video_file.delay(target_path, video_id)
        return f"File copy completed: {target_path}"
    except shutil.Error as e:
        video.set_error()
        return f"Error: {e}"


@app.task
def handle_video_file(video_path, video_id, remove_dir=None):
    video = Video.objects.get(id=video_id)
    filename_without_extension = os.path.splitext(os.path.basename(video_path))[0]
    try:
        ffmpeg_command = [
            'ffmpeg',
            '-i', video_path,
            '-vf', 'movie=watercat.png [watermark]; [in][watermark] overlay=W-w-10:H-h-10 [out]',
            '-c:a', 'copy',
            '-c:v', 'libx264',
            '-strict', 'experimental',
            '-b:a', '192k',
            '-b:v', '2000k',
            '-f', 'mp4',
            f'videos/handled/{filename_without_extension}_handle.mp4'
        ]

        subprocess.run(ffmpeg_command, check=True)
        video.set_completed()
        video.set_video_file(f'videos/handled/{filename_without_extension}_handle.mp4')

        if remove_dir:
            shutil.rmtree(os.path.dirname(video_path))
        else:
            os.remove(video_path)

        return f"Обработка файла {video_path} завершена"
    except subprocess.CalledProcessError as e:
        video.set_error()
        return f"Ошибка обработки файла {video_path}: {e}"

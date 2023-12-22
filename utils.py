import os


def find_video_file(directory):
    video_extensions = ['.mp4', '.avi', '.mkv', '.mov', '.wmv']

    for root, dirs, files in os.walk(directory):
        for file in files:
            if any(file.lower().endswith(ext) for ext in video_extensions):
                return os.path.join(root, file)
    return None

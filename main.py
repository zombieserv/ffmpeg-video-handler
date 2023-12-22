from datetime import datetime

from flask import Flask, request, jsonify
from mongoengine import DoesNotExist

from env import *
from models import Video
from services.VideoDownloader import VideoDownloader

app = Flask(__name__)

app.json.sort_keys = False  # disable sort keys


@app.route('/video', methods=['GET'])
def get_status_video():
    video_id = request.args.get('video_id')
    if not video_id:
        return {"error": "Video ID is missing in the request"}, 400

    try:
        video = Video.objects.get(id=video_id)
    except DoesNotExist:
        return {"error": "Video not found"}, 404
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}, 500

    video_information = {
        "id": str(video.id),
        "url": video.url,
        "name": video.name,
        "video_file": video.video_file,
        "status": video.status,
        "created_date": video.created_date,
        "status_changed": video.status_changed
    }

    return jsonify(video_information)


@app.route('/video', methods=['POST'])
def process_video():
    required_fields = ['url']
    form_data = request.get_json()

    if not all(field in form_data for field in required_fields):
        return jsonify({"error": f"Missing required fields: {', '.join(required_fields)}"}), 400

    video_url = form_data['url']

    video_data = {
        'url': video_url,
        'status': Video.PENDING,
        'created_date': datetime.now(),
        'status_changed': datetime.now()
    }
    db_video = Video(**video_data)
    db_video.save()
    video_id = str(db_video.id)

    video = VideoDownloader(video_url, video_id)
    video.parse().download()

    return {"id": video_id, "status": "success", "message": "Video added to queue."}


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

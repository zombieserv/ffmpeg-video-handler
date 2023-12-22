import os
from datetime import datetime

from mongoengine import connect, signals
from mongoengine import DynamicDocument, StringField, DateTimeField

DB_HOST = "mongodb://{}:{}@mongodb:27017".format(
    os.getenv('MONGODB_INITDB_ROOT_USERNAME'),
    os.getenv('MONGODB_INITDB_ROOT_PASSWORD'))

connect('ffmpeg-handler', host=DB_HOST)


class Video(DynamicDocument):
    PENDING = 'pending'
    DOWNLOADING = 'downloading'
    PROCESSING = 'processing'
    COMPLETED = 'completed'
    ERROR = 'error'

    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (DOWNLOADING, 'Downloading'),
        (PROCESSING, 'Processing'),
        (COMPLETED, 'Completed'),
        (ERROR, 'error'),
    ]

    url = StringField(required=True)
    name = StringField(required=False)
    video_file = StringField(required=False)
    status = StringField(choices=STATUS_CHOICES, default=PENDING)
    created_date = DateTimeField()
    status_changed = DateTimeField()

    def set_downloading(self):
        self.status = self.DOWNLOADING
        self.status_changed = datetime.now()
        signals.pre_save.send(self.__class__, document=self)
        self.save()

    def set_processing(self):
        self.status = self.PROCESSING
        self.status_changed = datetime.now()
        signals.pre_save.send(self.__class__, document=self)
        self.save()

    def set_completed(self):
        self.status = self.COMPLETED
        self.status_changed = datetime.now()
        signals.pre_save.send(self.__class__, document=self)
        self.save()

    def set_error(self):
        self.status = self.ERROR
        self.status_changed = datetime.now()
        signals.pre_save.send(self.__class__, document=self)
        self.save()

    def set_name(self, name):
        self.name = name
        self.save()

    def set_video_file(self, video_file):
        self.video_file = video_file
        self.save()

import os
from datetime import datetime

from django.conf import settings

from core.models import History


class HistoryManager(object):

    @classmethod
    def get_data_upload_history(cls):
        return [
            [
                history.uploader_nik,
                history.upload_time,
                os.path.normpath(os.path.join(settings.MEDIA_ROOT, history.file.name)),
            ] for history in History.objects.all() if history.payload_name == 'links_data'
        ]

    @classmethod
    def get_user_upload_history(cls):
        return [
            [
                history.uploader_nik,
                history.upload_time,
                os.path.normpath(os.path.join(settings.MEDIA_ROOT, history.file.name)),
            ] for history in History.objects.all() if history.payload_name == 'user'
        ]

    @classmethod
    def create_history(cls, payload_name, nik, f, dt):
        History.objects.create(uploader_nik=nik, upload_time=dt, payload_name=payload_name, file=f)






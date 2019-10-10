from core.models import History


class HistoryManager(object):

    @classmethod
    def get_data_upload_history(cls):
        return [
            [
                history.uploader_nik,
                history.upload_time,
            ] for history in History.objects.all() if history.payload_name == 'links_data'
        ]

    @classmethod
    def get_user_upload_history(cls):
        return [
            [
                history.uploader_nik,
                history.upload_time,
            ] for history in History.objects.all() if history.payload_name == 'user'
        ]

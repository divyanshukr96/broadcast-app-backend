from django.apps import AppConfig


class NoticeConfig(AppConfig):
    name = 'Notice'

    def ready(self):
        import Notice.signals

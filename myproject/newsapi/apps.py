# newsapi/apps.py
from django.apps import AppConfig

class NewsapiConfig(AppConfig):
    name = 'newsapi'

    def ready(self):
        import newsapi.signals  # Import the signals module to ensure it's ready

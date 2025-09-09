from django.apps import AppConfig
from django.utils.timezone import now
from datetime import timedelta

class PaymentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'payments'

    def ready(self):
        import payments.signals


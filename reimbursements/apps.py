from django.apps import AppConfig
from .scheduler import start

class ReimbursementsConfig(AppConfig):
    name = 'reimbursements'

    def ready(self):
        start()

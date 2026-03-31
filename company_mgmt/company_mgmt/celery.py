import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'company_mgmt.settings')

app = Celery('company_mgmt')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
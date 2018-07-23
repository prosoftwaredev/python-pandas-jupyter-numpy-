from __future__ import absolute_import

import sys
import os
import django

from celery import Celery
from benchmark.settings import base as settings


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'benchmark.settings.base')
django.setup()

app = Celery('tasks', backend=settings.CELERY_RESULT_BACKEND, broker=settings.CELERY_BROKER_URL)

app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

#sys.path.append('/work/dawr/bench/benchmarking-portal/data-science')

@app.task(bind=True)
def debug_task(self):
    print("Request: {0!r}".format(self.request))

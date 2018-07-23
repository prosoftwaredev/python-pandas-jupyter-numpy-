#!/bin/bash

echo [TIMING `date +"%F %R:%S"`] Starting celery workers
celery --app="benchmark.celery.app" worker --concurrency="${APP_WORKER_COUNT:-4}" -n "celery@$(hostname).${AMAZON_CURRENT_AZ}" &

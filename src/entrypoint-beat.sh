#!/bin/bash
echo [TIMING `date +"%F %R:%S"`] Starting celery beat
celery --app="benchmark.celery.app" beat &

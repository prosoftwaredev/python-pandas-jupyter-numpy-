#!/bin/bash

# run flower in background
# TODO: flower is commented, when we use it someone will uncomment it
# if [[  ${FLOWER_BASIC_AUTH} ]]
# then
#     echo [TIMING `date +"%F %R:%S"`] Starting flower
#     celery --app="$PACKAGE_NAME.celery_app.app" \
#     flower --basic_auth="${FLOWER_BASIC_AUTH}" \
#     --url_prefix="celery/flower" \
#     --address="0.0.0.0" &
#     KILL_LIST+=($!)
# else
#     echo "Skipping flower startup due to lack credentials variable"
# fi

echo [TIMING `date +"%F %R:%S"`] Starting nginx
/etc/init.d/nginx start

# run main worker in current thread
echo [TIMING `date +"%F %R:%S"`] Starting www workers

gunicorn "benchmark.wsgi:application" \
         --bind "0.0.0.0:8000" \
         --workers "${APP_WORKER_COUNT:-1}" \
         --log-level "info" \
         --reload \
         --timeout 600 \
         --max-requests=100 \
         --max-requests-jitter=50 &

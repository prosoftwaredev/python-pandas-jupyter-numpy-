FROM python:3.6.0

ENV DJANGO_STATIC_ROOT "/app/static_root/"
ENV PYTHONPATH $PYTHONPATH:/app/data-science
# These dependencies are baggage we found we need often enough to include
# them in our base image
RUN apt-get update && \
    apt-get install -y wget \
                       libpq-dev \
                       python-dev \
                       build-essential \
                       libxml2-dev \
                       libxslt1-dev \
                       libjpeg-dev \
                       graphviz \
                       graphviz-dev \
                       pkg-config \
                       postgresql-client \
                       git \
                       libgraphviz-dev \
                       libcgraph6 \
                       nginx && \
    apt-get clean && \
    rm -rf /tmp/* /var/tmp/* /usr/share/man /tmp/* /var/tmp/* \
       /var/cache/apk/* /var/log/* /var/lib/apt/lists/* ~/.cache

# Include nginx logs in container logs
RUN mkdir -p /var/log/nginx && \
    ln -sf /dev/stdout /var/log/nginx/access.log && \
    ln -sf /dev/stderr /var/log/nginx/error.log

ADD ./src /app
ADD ./devops/docker/nginx.conf /etc/nginx/nginx.conf
ADD ./devops/docker/scripts /app/docker
ADD ./data-science /app/data-science

# Install python requirements
RUN pip install -r /app/requirements.txt > /tmp/pip-requirements-install.log
RUN pip install -r /app/data-science/requirements.txt > /tmp/pip-data-science-requirements-install.log

# Collect up static files
RUN export DJANGO_DEBUG="True" && \
    cd /app && python manage.py collectstatic -i babel* \
                                   -i webpac* \
                                   -i uglify* \
                                   -i sha* \
                                   -i src \
                                   -i crypto-browserify \
                                   -i core-js \
                                   -i docs \
                                   -i media \
                                   --noinput > /tmp/collectstatic.log

# can be avoided if entrypoint.sh file in the repo has +x flag?
RUN chmod +x /app/docker/entrypoint.sh

ENTRYPOINT ["/app/docker/entrypoint.sh"]

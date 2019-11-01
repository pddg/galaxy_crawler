FROM python:3.7-slim-buster

ENV PROJECT_DIR /opt/galaxy/

RUN pip3 install --no-cache-dir "pipenv==2018.11.26"

COPY . ${PROJECT_DIR}
WORKDIR ${PROJECT_DIR}

RUN apt-get update && \
    apt-get install -y \
        libpq-dev \
        gcc \
        g++ \
        git && \
    pipenv install --system --deploy && \
    pip3 install --no-cache-dir \
        psycopg2-binary==2.8.3 \
        pymysql==0.9.3 && \
    apt-get remove --purge -y \
        libpq-dev \
        gcc \
        g++ && \
    apt-get clean -y && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/list/*

CMD ["/usr/local/bin/galaxy"]

FROM python:3.7-slim-buster

ENV PROJECT_DIR /opt/galaxy/

RUN apt-get update && \
    apt-get install -y \
        libpq-dev \
        git && \
    pip3 install --no-cache-dir \
        "pipenv==2018.11.26" \
        psycopg2-binary==2.8.3 \
        pymysql==0.9.3 \
        jupyter==1.0.0 \
        seaborn==0.9.0 && \
    apt-get remove --purge -y \
        libpq-dev && \
    apt-get clean -y && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/list/*

COPY . ${PROJECT_DIR}
WORKDIR ${PROJECT_DIR}

RUN apt-get update && \
    apt-get install -y \
        gcc \
        g++ && \
    pipenv install --system --deploy && \
    apt-get remove --purge -y \
        gcc \
        g++ && \
    apt-get clean -y && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/list/*

CMD ["/usr/local/bin/galaxy"]

FROM python:3.8-alpine

ENV PROJECT_DIR /opt/galaxy/

RUN pip3 install --no-cache-dir "pipenv==2018.11.26"

COPY . ${PROJECT_DIR}
WORKDIR ${PROJECT_DIR}

RUN apk update && \
    apk add postgresql-libs && \
    apk add --virtual .build-deps gcc musl-dev postgresql-dev && \
    pipenv install --system --deploy && \
    pip3 install --no-cache-dir \
        psycopg2-binary==2.8.3 \
        pymysql==0.9.3 && \
    pip3 install -e . && \
    apk --purge del .build-deps

CMD ["/usr/local/bin/galaxy"]

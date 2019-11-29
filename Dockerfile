FROM python:3.7-slim-buster

ENV PROJECT_DIR /opt/galaxy/

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        gcc \
        g++ \
        libpq-dev \
        git && \
    curl -sL https://deb.nodesource.com/setup_12.x | bash - && \
    apt-get install -y --no-install-recommends \
        nodejs && \
    pip3 install --no-cache-dir \
        "pipenv==2018.11.26" \
        psycopg2-binary==2.8.3 \
        pymysql==0.9.3 \
        jupyterlab==1.2.3 \
        jupyterlab-code-formatter==0.7.0 \
        pytablewriter==0.46.1 \
        black==19.10b0 \
        seaborn==0.9.0 && \
    jupyter labextension install \
        @ryantam626/jupyterlab_code_formatter \
        @lckr/jupyterlab_variableinspector && \
    jupyter serverextension enable --py jupyterlab_code_formatter && \
    apt-get remove --purge -y \
        gcc \
        g++ \
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

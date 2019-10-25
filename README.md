# Crawling tool for ansible galaxy

This tool is currently under development. There are some bugs and few features.

## Environment

- Python >= 3.7
- pipenv

The environment setup automatically by following command

```bash
$ pipenv install
```

## How to use

```bash
$ pipenv run galaxy --help
usage: galaxy [-h] [--version] [--debug] [--log-dir LOG_DIR]
              {crawl,db,load} ...

Ansible Galaxy crawler

optional arguments:
  -h, --help         show this help message and exit
  --version          Show version

LOGGING:
  --debug            Enable debug logging
  --log-dir LOG_DIR  Log output directory

Sub commands:
  {crawl,db,load}
    crawl            Crawl Ansible Galaxy API
    db               Sub command for DB
    load             Role info from JSON to DB
```

### 1. Obtain json objs from Ansible Galaxy

```bash
$ pipenv run galaxy crawl \
    /path/to/output \
    --interval 5
```

`crawl` command will take many hours.

### 3. Insert them into DB

`load` command try to insert them into database. Following databases are supported.

- PostgreSQL
    - `psycopg2-binary` is required
- MySQL/MariaDB
    - `pymysql` is required
- SQLite3

```bash
$ pipenv galaxy load \
    /path/to/json_dir \
    --storage postgresql://user:password@host:port/db \
    --interval 5
```

You can specify the information of database by environment variable.

| Env var            | Default value |
| ------------------ | ------------- |
| GALAXY_DB_TYPE     | postgres     |
| GALAXY_DB_HOST     | 127.0.0.1     |
| GALAXY_DB_PORT     | 5432          |
| GALAXY_DB_NAME     | galaxy        |
| GALAXY_DB_USER     | galaxy        |
| GALAXY_DB_PASSWORD | galaxy        |
| GALAXY_DB_PATH     | sqlite3.db    |

**NOTE**: This command will delete the tables in the specified database.

## Author

pddg

## License

MIT

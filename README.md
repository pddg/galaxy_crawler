# Crawling tool for ansible galaxy

This tool is currently under development. There are some bugs and few features.

## Environment

- Python >= 3.7

```bash
$ pip isntall -e .
# For MySQL/MariaDB user
$ pip install -e .[mysql]
# For PostgreSQL user
# This will require that PostgreSQL's libraries are installed
$ pip install -e .[postgres]
```

## How to use

```bash
$ galaxy --help
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
$ galaxy crawl \
    /path/to/output \
    --interval 5
```

`crawl` command will take many hours.

### 2. Insert them into DB

`load` command try to insert them into database. Following databases are supported.

- PostgreSQL
    - `psycopg2-binary` is required
- MySQL/MariaDB
    - `pymysql` is required
- SQLite3

```bash
$ galaxy load \
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

### 3. Clone the roles

If `--date-from`/`--date-to` is not specified, use the oldest/newest datetime of obtained roles. 

```bash
$ galaxy repo clone /path/to/clone \
    --interval 5 \
    --percentile 0.9 \
    --date-from 2018/10/22
```

Repositories are cloned by [ghq](https://github.com/motemen/ghq). It is downloaded automatically.

```bash
$ tree -L 3 /path/to/clone
repos
├── 2019-11-01_12-26-23.log
└── github.com
    ├── user1
    │   ├── role1
    │   ├── role2
    │   └── role3
    └── user2
        └── role4
```

## Database Scheme

![img](scheme.svg)

## Author

pddg

## License

MIT

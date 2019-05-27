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
$ pipenv run python -m galaxy_crawler.cli start -h
usage: cli.py start [-h] [--debug] [--log-dir LOG_DIR] [--version {v1}]
                    [--interval INTERVAL] [--retry RETRY]
                    [--format {json} [{json} ...]]
                    [--order-by {download,star,contributor_name,relevance,fork,watcher}]
                    [--inverse]
                    output_dir

positional arguments:
  output_dir            Path to output

optional arguments:
  -h, --help            show this help message and exit
  --version {v1}        The API version of galaxy.ansible.com
  --interval INTERVAL   Fetch interval (default=10)
  --retry RETRY         Number of retrying (default=3)
  --format {json} [{json} ...]
                        Output format (default=['json'])
  --order-by {download,star,contributor_name,relevance,fork,watcher}
                        Query order (default=download). It is a descending
                        order by default.
  --inverse             If this specified, make the order of query inverse

LOGGING:
  --debug               Enable debug logging
  --log-dir LOG_DIR     Log output directory
```

Currently, `--order-by donwload` only works fine (threshold is fixed (500)).

## Author

pddg

## License

MIT

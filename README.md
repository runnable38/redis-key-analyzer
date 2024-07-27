# redis-key-analyzer

## Overview

`redis-key-analyzer` is a tool designed to analyze Redis keys, providing detailed statistics on key patterns, memory usage, TTL (Time to Live), and more. This tool is useful for understanding the distribution and characteristics of keys in a Redis database, which can help in optimizing and managing Redis instances.

## Features

- Analyze Redis keys based on patterns, prefixes, and separators.
- Collect statistics on key types, memory usage, and TTL.
- Support for read-only Redis clusters.
- Configurable batch size and sleep intervals for large datasets.

## Installation

To install `redis-key-analyzer`, use pip:

```bash
pip install rka
```

## Usage

You can use the `redis-key-analyzer` via the command line interface (CLI). Below are the available options:

```bash
Usage: redis-key-analyzer [OPTIONS]

Options:
  --host TEXT          Redis host. Default is 'localhost'.
  --port INTEGER       Redis port. Default is 6379.
  --db INTEGER         Redis database. Default is 0.
  --read-only, -ro     Check read-only cluster.
  --match, -m TEXT     Redis key pattern. Default is '*'.
  --batch-size INTEGER Batch size. Default is 1000.
  --prefix TEXT        Prefixes for key pattern. Example: --prefix 'prefix1 prefix2'.
  --separator TEXT     Separators for key pattern. Default is ':'.
  --limit INTEGER      Limit total keys. -1 for no limit. Default is -1.
  --sleep INTEGER      Sleep seconds between batches. -1 for no sleep. Default is -1.
  --help               Show this message and exit.
```

Search 

```bash
rka --host localhost [--port 6379] [--db 0] [-m '*']

+-------------+--------+-------+---------+---------+-------+--------------+-----------+------------+------------+----------+----------+--------------+
| pattern     | dtype  |  ttl  | avg_ttl | max_ttl | count | total_memory | memory_hu | memory_avg | memory_max | size_avg | size_max | key(max_ttl) |
+-------------+--------+-------+---------+---------+-------+--------------+-----------+------------+------------+----------+----------+--------------+
| my-set      |  set   | NOTTL |    -1   |    -1   |   1   |          272 |  272.0  B |    272     |    272     |    3     |    3     | my-set       |
| my-list     |  list  | NOTTL |    -1   |    -1   |   1   |          223 |  223.0  B |    223     |    223     |    14    |    14    | my-list      |
| foos:<*>    | string |  TTL  |   524   |   984   |   3   |          183 |  183.0  B |     61     |     61     |    3     |    3     | foos:123     |
| my-hash     |  hash  | NOTTL |    -1   |    -1   |   1   |           87 |   87.0  B |     87     |     87     |    2     |    2     | my-hash      |
| my-zset     |  zset  | NOTTL |    -1   |    -1   |   1   |           83 |   83.0  B |     83     |     83     |    2     |    2     | my-zset      |
| user.sc:<*> |  hash  | NOTTL |    -1   |    -1   |   1   |           75 |   75.0  B |     75     |     75     |    1     |    1     | user.sc:123  |
| my-string   | string | NOTTL |    -1   |    -1   |   1   |           61 |   61.0  B |     61     |     61     |    3     |    3     | my-string    |
+-------------+--------+-------+---------+---------+-------+--------------+-----------+------------+------------+----------+----------+--------------+
```
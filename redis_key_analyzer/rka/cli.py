import re

import click

from rka.redis_key_analyzer import start_redis_key_analyzer


@click.command()
@click.option("--host", default="localhost", help="Redis host.")
@click.option("--port", default=6379, help="Redis port.")
@click.option("--db", default=0, help="Redis database.")
@click.option("--read-only", "-ro", is_flag=True, help="Check read-only cluster")
@click.option("--match", "-m", default="*", help="Redis key pattern")
@click.option("--batch-size", default=1000, help="Batch size")
@click.option(
    "--prefix",
    default=None,
    help="prefixes for key pattern. ex) --prefix 'prefix1 prefix2'",
)
@click.option("--separator", default=":", help="separators for key pattern")
@click.option("--limit", default=-1, help="Limit total keys. -1 for no limit")
@click.option(
    "--sleep", default=-1, help="Sleep seconds between batches. -1 for no sleep"
)
def main(
    host: str,
    port: int,
    db: int,
    read_only: bool,
    match: str,
    batch_size: int,
    prefix: str,
    separator: str,
    limit: int,
    sleep: int,
) -> None:
    prefixes = re.split(r"\s+", prefix) if prefix else None
    separators = [separator]
    start_redis_key_analyzer(
        host, port, db, read_only, match, prefixes, separators, batch_size, limit, sleep
    )

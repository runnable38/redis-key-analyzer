import re
import sys
from typing import Iterable, Union

import redis

from rka.model import RedisKeyInfo, RedisKeyPatternStat
from rka.report import generate_report
from rka.scan import scan_redis_key_info

NUMBER_PLACE_HOLDER = "<N>"
SUFFIX_PLACE_HOLDER = "<*>"


def start_redis_key_analyzer(
    host,
    port,
    db,
    read_only,
    match,
    prefixes: list[str] = None,
    separators: list[str] = None,
    batch_size=1000,
    limit=-1,
    sleep_seconds=-1,
):
    print(
        f"Starting redis key analyzer...  {host=}, {port=}, {db=}, {batch_size=}, {match=}, {read_only=}, {prefixes=}, {separators=}, {limit=}, {sleep_seconds=}"
    )
    conn = redis.Redis(host=host, port=port, db=db)

    if read_only:
        _check_read_only(conn)

    key_infos = scan_redis_key_info(
        conn=conn,
        db=db,
        match=match,
        batch_size=batch_size,
        sleep_seconds=sleep_seconds,
        limit=limit,
    )
    stats = analyze_key_info(key_infos, prefixes, separators)
    generate_report(list(stats.values()), filepath=None)


def analyze_key_info(
    key_infos: Iterable[RedisKeyInfo],
    prefixes: list[str] = None,
    separators: list[str] = None,
):
    stat = {}
    for key_info in key_infos:
        pattern = _get_key_pattern(
            key_info.key, prefixes=prefixes, separators=separators
        )
        ttl_type = _get_ttl_type(key_info.ttl)
        if ttl_type is None:
            continue
        unique_key = (pattern, key_info.dtype, ttl_type)
        if unique_key not in stat:
            stat[unique_key] = RedisKeyPatternStat(
                pattern=pattern,
                key=key_info.key,
                ttl=ttl_type,
                total_ttl=0,
                max_ttl=key_info.ttl,
                dtype=key_info.dtype,
            )
        stat[unique_key].count = stat[unique_key].count + 1
        stat[unique_key].memory += key_info.memory
        if stat[unique_key].max_memory < key_info.memory:
            stat[unique_key].max_memory = key_info.memory
        stat[unique_key].size += key_info.size
        if stat[unique_key].max_size < key_info.size:
            stat[unique_key].max_size = key_info.size
        if stat[unique_key].max_ttl < key_info.ttl:
            stat[unique_key].max_ttl = key_info.ttl
            stat[unique_key].max_ttl_key = key_info.key

        stat[unique_key].total_ttl += key_info.ttl
    return stat


def _check_read_only(conn: redis.Redis):
    # Redis 5.0+에서는 "replica"가 표준 용어
    if conn.info().get("role") not in ["slave", "replica"]:
        print(f"Aborted the operation on non-readonly redis at host: {conn}")
        sys.exit(1)


def _get_ttl_type(ttl: int) -> Union[str, None]:
    if ttl == -1:
        return "NOTTL"
    elif ttl == -2:
        return None
    elif ttl >= 0:
        return "TTL"
    else:
        return None


def _get_key_pattern(
    key: str,
    number_place_holder: str = NUMBER_PLACE_HOLDER,
    prefixes: list[str] = None,
    separators: list[str] = None,
    suffix_place_holder: str = SUFFIX_PLACE_HOLDER,
) -> str:
    key, changed = _replace_prefix(key, prefixes=prefixes, separators=separators, suffix_place_holder=suffix_place_holder)
    if changed:
        return key
    return _replace_number(key, number_place_holder=number_place_holder)


def _replace_number(key: str, number_place_holder: str) -> str:
    return re.sub(r"\d+", number_place_holder, key)


def _replace_prefix(
    key: str,
    prefixes: list[str],
    separators: list[str],
    suffix_place_holder: str,
) -> tuple[str, bool]:
    if prefixes:
        for prefix in prefixes:
            if key.startswith(prefix):
                pattern = prefix + suffix_place_holder
                return pattern, True
    if separators:
        for separator in separators:
            if separator in key:
                pattern = key[: key.find(separator) + len(separator)] + suffix_place_holder
                return pattern, True
    return key, False

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
    separator: str = None,
    separator_max_depth: int = 1,
    batch_size=1000,
    limit=-1,
    sleep_seconds=-1,
):
    print(
        f"Starting redis key analyzer...  {host=}, {port=}, {db=}, {batch_size=}, {match=}, {read_only=}, {prefixes=}, {separator=}, {separator_max_depth=}, {limit=}, {sleep_seconds=}"
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
    stats = analyze_key_info(key_infos, prefixes, separator, separator_max_depth)
    generate_report(list(stats.values()), filepath=None)


def analyze_key_info(
    key_infos: Iterable[RedisKeyInfo],
    prefixes: list[str] = None,
    separator: str = None,
    separator_max_depth: int = 1,
):
    stat = {}
    for key_info in key_infos:
        pattern = _get_key_pattern(
            key_info.key, prefixes=prefixes, separator=separator, separator_max_depth=separator_max_depth
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
    separator: str = None,
    separator_max_depth: int = 1,
    suffix_place_holder: str = SUFFIX_PLACE_HOLDER,
) -> str:
    key, changed = _replace_prefix(key, prefixes=prefixes, separator=separator, separator_max_depth=separator_max_depth, suffix_place_holder=suffix_place_holder)
    if changed:
        return key
    return _replace_number(key, number_place_holder=number_place_holder)


def _replace_number(key: str, number_place_holder: str) -> str:
    return re.sub(r"\d+", number_place_holder, key)


def _replace_prefix(
    key: str,
    prefixes: list[str],
    separator: str,
    separator_max_depth: int,
    suffix_place_holder: str,
) -> tuple[str, bool]:
    if prefixes:
        for prefix in prefixes:
            if key.startswith(prefix):
                pattern = prefix + suffix_place_holder
                return pattern, True
    if separator:
        matches = find_all_occurrences(key, separator, limit=separator_max_depth)
        if matches:
            pattern = key[:matches[-1] + len(separator)] + suffix_place_holder
            return pattern, True
    return key, False


def find_all_occurrences(key: str, pattern: str, limit: int | None = None) -> list[int]:
    """
    key: 입력 문자열
    pattern: 찾을 패턴
    limit: 찾을 최대 횟수 (None이면 제한 없음)
    반환값: 매치 시작 인덱스들의 리스트
    """
    if not pattern:
        raise ValueError("pattern 길이는 1 이상이어야 합니다.")

    res = []
    i = 0
    L = len(pattern)
    while True:
        j = key.find(pattern, i)
        if j == -1:
            break
        res.append(j)
        if limit is not None and len(res) >= limit:
            break
        i = j + L  # 겹치지 않게 다음 검색 시작 위치 이동
    return res

import math
from collections import defaultdict

from prettytable import PrettyTable

from rka.model import RedisKeyPatterStat


def generate_report_rows(key_pattern_infos: list[RedisKeyPatterStat]):
    fields = [
        "pattern",
        "dtype",
        "ttl",
        "avg_ttl",
        "max_ttl",
        "count",
        "total_memory",
        "memory_hu",
        "memory_avg",
        "memory_max",
        "size_avg",
        "size_max",
        "key(max_ttl)",
    ]

    rows = [
        (
            row.pattern,
            row.dtype,
            row.ttl,
            row.total_ttl // row.count if row.count > 0 else 0,
            row.max_ttl,
            row.count,
            row.memory,
            readable_bytes(row.memory) if row.memory > 0 else row.memory,
            row.memory // row.count,
            row.max_memory,
            row.size // row.count,
            row.max_size,
            row.max_ttl_key,
        )
        for row in key_pattern_infos
        if (True or row.dtype is not None and row.ttl is not None)
    ]
    rows = [_handle_none(row) for row in rows]
    return fields, rows


def generate_report(key_pattern_infos: list[RedisKeyPatterStat], filepath: str = None):
    key_pattern_infos = sort_key_pattern_infos(key_pattern_infos)
    fields, rows = generate_report_rows(key_pattern_infos)
    draw_with_pretty_table(fields, rows)


def sort_key_pattern_infos(rows: list[RedisKeyPatterStat]) -> list[RedisKeyPatterStat]:
    """ "
    sort by total memory in the same pattern group
    """
    total_memory_by_pattern = defaultdict(int)
    for row in rows:
        total_memory_by_pattern[row.pattern] += row.memory

    return sorted(
        rows,
        key=lambda row: (total_memory_by_pattern[row.pattern], row.memory),
        reverse=True,
    )


def draw_with_pretty_table(fields, rows):
    table = PrettyTable()
    table.field_names = fields
    table.add_rows(rows)
    table.align["pattern"] = "l"
    table.align["total_memory"] = "r"
    table.align["memory_hu"] = "r"
    table.align["key(max_ttl)"] = "l"

    print(table)


def _handle_none(row):
    return [e if e is not None else "None" for e in row]


def readable_bytes(num, suffix="B"):
    magnitude = int(math.floor(math.log(num, 1024)))
    val = num / math.pow(1024, magnitude)
    if magnitude > 7:
        return "{:.1f}{}{}".format(val, "Y", suffix)
    return "{:3.1f} {}{}".format(
        val, [" ", "K", "M", "G", "T", "P", "E", "Z"][magnitude], suffix
    )

import dataclasses


@dataclasses.dataclass
class RedisKeyInfo:
    key: str
    dtype: str
    ttl: int
    memory: int
    size: int

    @classmethod
    def parse_obj(cls, obj):
        return cls(**obj)


@dataclasses.dataclass
class RedisKeyPatterStat:
    pattern: str = None
    dtype: str = None
    ttl: str = None
    count: int = 0
    memory: int = 0
    max_memory: int = 0
    total_ttl: int = None
    max_ttl: int = None
    size: int = 0
    max_size: int = 0
    key: str = None
    max_ttl_key: str = None

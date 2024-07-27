import time

from tqdm import tqdm

from rka.model import RedisKeyInfo


def scan_redis_key_info(
    conn, db, match, batch_size, limit: int = -1, sleep_seconds: float = -1
):

    conn.execute_command("SELECT", db)

    info = conn.info()
    total_keys = info.get("db" + str(db), {}).get("keys", 0)

    print(f"Total number of keys: {total_keys} in db={db}")

    script = """
            local cursor = ARGV[1]
            local result = {}

            local scanResult = redis.call('SCAN', cursor, 'MATCH', 'MATCH_PATTERN','COUNT', BATCH_SIZE)
            cursor = scanResult[1]

            local function getValueByKeyType(key, key_type)
                if key_type == 'string' then
                    return redis.call('GET', key)
                elseif key_type == 'list' then
                    return redis.call('LRANGE', key, 0, -1)
                elseif key_type == 'set' then
                    return redis.call('SMEMBERS', key)
                elseif key_type == 'zset' then
                    return redis.call('ZRANGE', key, 0, -1, 'WITHSCORES')
                elseif key_type == 'hash' then
                    return redis.call('HGETALL', key)
                else
                    return 'UNKNOWN'
                end
            end

            local function getSizeByKeyType(key, key_type)
                if key_type == 'string' then
                    return redis.call('STRLEN', key)
                elseif key_type == 'list' then
                    return redis.call('LLEN', key)
                elseif key_type == 'set' then
                    return redis.call('SCARD', key)
                elseif key_type == 'zset' then
                    return redis.call('ZCARD', key)
                elseif key_type == 'hash' then
                    return redis.call('HLEN', key)
                else
                    return 0
                end
            end

            for i, key in ipairs(scanResult[2]) do
                local key_type = redis.call('TYPE', key)['ok']
                local ttl = redis.call('TTL', key)
                local memory = redis.call('MEMORY', 'USAGE', key)
                local size = getSizeByKeyType(key, key_type)
                table.insert(result, {key, key_type, ttl, memory, size})
            end

            return {cursor, result}
        """
    script = script.replace("MATCH_PATTERN", match)
    script = script.replace("BATCH_SIZE", str(batch_size))

    cursor = b"0"
    count = 0
    total_count = limit if limit > 0 else total_keys

    with tqdm(total=total_count, desc="Scanning keys", unit="key") as pbar:
        while True:
            cursor, key_infos = conn.eval(script, 0, cursor)
            for key_info in key_infos:
                yield RedisKeyInfo.parse_obj(
                    {
                        "key": key_info[0].decode(),
                        "dtype": key_info[1].decode(),
                        "ttl": key_info[2],
                        "memory": key_info[3],
                        "size": key_info[4],
                    }
                )
                count += 1
                pbar.update(1)

                if 0 < limit <= count:
                    break

            if sleep_seconds > 0:
                time.sleep(sleep_seconds)

            if cursor == b"0":
                break

import os
import json
import redis.asyncio as aioredis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

async def get_redis():
    return aioredis.from_url(REDIS_URL, decode_responses=True)

async def get_cache(key: str):
    r = await get_redis()
    value = await r.get(key)
    print(f"Кэш запрос {key}: {'найден' if value else 'не найден'}")
    if value is not None:
        return json.loads(value)
    return None

async def set_cache(key: str, value, expire: int = 60):
    r = await get_redis()
    try:
        serialized = json.dumps(value)
        await r.set(key, serialized, ex=expire)
        print(f"Кэш сохранён: {key}")
    except Exception as e:
        print(f"Ошибка кэша: {e}")

async def delete_cache(key: str):
    r = await get_redis()
    await r.delete(key)
import asyncio

from services.dependencies.redis import init_redis_pool


# import pkgutil
# import sys
#
# search_path = ['.'] # Используйте None, чтобы увидеть все модули, импортируемые из sys.path
# all_modules = [x[1] for x in pkgutil.iter_modules(path=search_path)]
# print(all_modules, sys.path[0])

async def redis_test_cache():
    pool = await init_redis_pool("localhost", "").__anext__()
    if not (value := await pool.hget("cache", "user")):
        print("GO HERE")
        value = await pool.hset("cache", "user", "FakeUser")
    print(value)


print(asyncio.run(redis_test_cache()))

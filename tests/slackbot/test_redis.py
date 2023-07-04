import aioredis
import pytest 
from slackbot import app




@pytest.mark.skip
async def test_redis_cache():
    redis = app.get_cache() 
    # await redis.set("test", "test")
    # actual = await redis.get("test")
    # assert actual == "test"
    redis.close()
    
    # async with await app.get_cache() as redis:
    #     await redis.set("test", "test")
    #     assert await redis.get("test") == "test"
    #     await redis.delete("test")
    #     assert await redis.get("test") == None

    
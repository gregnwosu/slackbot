
import pytest 
from slackbot import app


@pytest.mark.asyncio
async def test_redis_cache():
    redis = app.get_cache()
    await redis.set("test", "nukkk")
    actual = await redis.get("test")
    assert actual == "nukkk"
    await redis.close()
    

    
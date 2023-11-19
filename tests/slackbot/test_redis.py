
import pytest 
from slackbot import  utils

from dotenv import find_dotenv, load_dotenv
from slackbot.llm import LLM

load_dotenv(find_dotenv())
@pytest.mark.skip
@pytest.mark.asyncio
async def test_redis_cache():
  async with utils.get_cache() as redis:
    await redis.set("test", "nukkk")
    actual = await redis.get("test")
    assert actual == "nukkk"
    await redis.close()
    

    
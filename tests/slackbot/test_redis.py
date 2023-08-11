
import pytest 
from slackbot import app
from langchain.memory import ConversationSummaryBufferMemory
from langchain import OpenAI
from dotenv import find_dotenv, load_dotenv
from slackbot.llm import LLM

load_dotenv(find_dotenv())
@pytest.mark.skip
@pytest.mark.asyncio
async def test_redis_cache():
  async with app.get_cache() as redis:
    await redis.set("test", "nukkk")
    actual = await redis.get("test")
    assert actual == "nukkk"
    await redis.close()
    

@pytest.mark.asyncio
async def test_cache_memory():
        redis =app.get_cache() 
        await redis.flushall()
        memory=ConversationSummaryBufferMemory(llm=LLM.GPT4.value)
        await app.cache_channel_memory(channel_id="test2", channel_memory_cache=redis, memory=memory)
        channel_memory = await app.get_memory_from_cache(channel_id="test2", channel_memory_cache=redis)
        assert channel_memory is not None
        assert isinstance(channel_memory, ConversationSummaryBufferMemory)

    
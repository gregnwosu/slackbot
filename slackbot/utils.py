
import datetime as dt
import functools
import json
import os
from typing import Optional

import aioredis
from dotenv import find_dotenv, load_dotenv

# from aiocache.serializers import PickleSerializer
# from aiocache.serializers import PickleSerializer



from slackbot.llm import LLM

# Load environment variables from .env file
load_dotenv(find_dotenv())

SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_SIGNING_SECRET = os.environ["SLACK_SIGNING_SECRET"]
SLACK_BOT_USER_ID = os.environ["SLACK_BOT_USER_ID"]
REDIS_URL = os.environ["REDIS_URL"]
REDIS_KEY = os.environ["REDIS_KEY"]


def get_cache() -> aioredis.Redis:
    return aioredis.Redis(
        host=REDIS_URL,
        password=REDIS_KEY,
        ssl=True,
        port=6380,
        db=0,
        decode_responses=True,
    )


async def cache_channel_memory(channel_id: str, channel_memory_cache: aioredis.Redis, memory: ConversationSummaryBufferMemory):
    channel_memory_json: str = json.dumps(messages_to_dict(memory.chat_memory.messages))
    await channel_memory_cache.set(
                f"channel_memory:{channel_id}", channel_memory_json, ex=dt.timedelta(hours=5)
            )
    




# async def redis_memory_decorator(func):
#     @functools.wraps(func)
#     async def wrapper(channel_id: str, *args, **kwargs):
#         # Get a Redis cache instance (assuming get_cache is defined in your utilities)
#         async with get_cache() as channel_memory_cache:

            
#             # 1. Retrieve memory from Redis
#             memory = await get_memory_for_channel(channel_id=channel_id)
            
#             # 2. Call the decorated function with the memory object
#             result = await func(channel_id, memory, *args, **kwargs)
            
#             # 3. Save the updated memory back to Redis
#             await cache_channel_memory(channel_id=channel_id, channel_memory_cache=channel_memory_cache, memory=memory)
            
#             return result
#     return wrapper


# python
# Copy code
# @redis_memory_decorator
# async def some_function(channel_id: str, memory: ConversationSummaryBufferMemory, some_other_arg):
#     # Do something with the memory
#     ...
#     return some_result
# When some_function is called, the redis_memory_decorator will automatically handle reading the memory from Redis and saving it back after the function completes.

# Note: Ensure that the get_cache function is available in the scope where the decorator is used.



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



# python
# Copy code
# @redis_memory_decorator
# async def some_function(channel_id: str, memory: ConversationSummaryBufferMemory, some_other_arg):
#     # Do something with the memory
#     ...
#     return some_result
# When some_function is called, the redis_memory_decorator will automatically handle reading the memory from Redis and saving it back after the function completes.

# Note: Ensure that the get_cache function is available in the scope where the decorator is used.


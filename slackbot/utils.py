
import datetime as dt
import functools
import json
import os
from typing import Optional

import aioredis
from dotenv import find_dotenv, load_dotenv
from langchain.memory import ConversationSummaryBufferMemory

# from aiocache.serializers import PickleSerializer
from langchain.memory.chat_message_histories.in_memory import ChatMessageHistory
from langchain.schema import messages_from_dict, messages_to_dict

from slackbot.llm import LLM

import sys
import os 
import json
import datetime as dt

import functools
from functools import wraps
from aiocache import cached
import aioredis
import time
from fastapi import FastAPI, Request
import requests
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.signature import SignatureVerifier
from slack_sdk.errors import SlackApiError
from slack_bolt.adapter.fastapi.async_handler import AsyncSlackRequestHandler
from slack_bolt.authorization import AuthorizeResult
from slack_bolt.async_app import AsyncApp
from starlette.responses import Response
from fastapi import FastAPI, Request, HTTPException, Response
from slackbot.parsing.appmention.event import AppMentionEvent
from slackbot.tools import Agents
from langchain.memory import ConversationSummaryBufferMemory
from langchain import OpenAI
from dotenv import find_dotenv, load_dotenv
import logging
from typing import Optional
from langchain.schema import messages_from_dict, messages_to_dict
# from aiocache.serializers import PickleSerializer
from slackbot.parsing.file.event import FileInfo, FileEvent
from slackbot.parsing.file.model import MimeType
from slackbot.parsing.message.event import MessageSubType
import slackbot.functions as functions
from slackbot.tools import Conversation
from langchain.memory.chat_message_histories.in_memory import ChatMessageHistory
from typing import List, Optional
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
    
async def get_memory_from_cache(channel_id: str, channel_memory_cache: aioredis.Redis) -> Optional[ConversationSummaryBufferMemory]:
    channel_memory_json: Optional[str] = await channel_memory_cache.get(f"channel_memory:{channel_id}")
    if not channel_memory_json:
        return None
    messages_dicts = json.loads(channel_memory_json)
    
    messages = messages_from_dict(messages_dicts)
    chat_memory: ChatMessageHistory=ChatMessageHistory(messages=messages)

    return  ConversationSummaryBufferMemory(llm=LLM.GPT4.value, chat_memory=chat_memory) 

async def get_memory_for_channel(channel_id: str) -> ConversationSummaryBufferMemory:
    async with get_cache() as channel_memory_cache:
        channel_memory: ConversationSummaryBufferMemory= await get_memory_from_cache(channel_id=channel_id, channel_memory_cache=channel_memory_cache)
        if not channel_memory:
            channel_memory=ConversationSummaryBufferMemory(llm=LLM.GPT4.value)
            await cache_channel_memory(channel_id=channel_id, channel_memory_cache=channel_memory_cache, memory=channel_memory)
        return channel_memory



async def redis_memory_decorator(func):
    @functools.wraps(func)
    async def wrapper(channel_id: str, *args, **kwargs):
        # Get a Redis cache instance (assuming get_cache is defined in your utilities)
        async with get_cache() as channel_memory_cache:

            
            # 1. Retrieve memory from Redis
            memory = await get_memory_for_channel(channel_id=channel_id)
            
            # 2. Call the decorated function with the memory object
            result = await func(channel_id, memory, *args, **kwargs)
            
            # 3. Save the updated memory back to Redis
            await cache_channel_memory(channel_id=channel_id, channel_memory_cache=channel_memory_cache, memory=memory)
            
            return result
    return wrapper


# python
# Copy code
# @redis_memory_decorator
# async def some_function(channel_id: str, memory: ConversationSummaryBufferMemory, some_other_arg):
#     # Do something with the memory
#     ...
#     return some_result
# When some_function is called, the redis_memory_decorator will automatically handle reading the memory from Redis and saving it back after the function completes.

# Note: Ensure that the get_cache function is available in the scope where the decorator is used.


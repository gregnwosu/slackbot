
from slackbot.parsing.slackapi import FileEvent, FileInfo
import os
from slack_sdk import WebClient
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.errors import SlackApiError
from slack_sdk.signature import SignatureVerifier
from fastapi import FastAPI, Request, Response
from slack_bolt import App
from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.fastapi.async_handler import AsyncSlackRequestHandler
from fastapi import FastAPI, Request, HTTPException
import slack_bolt
from dotenv import find_dotenv, load_dotenv

from functions import draft_email
import logging
from functools import lru_cache, wraps
import time
import asyncio
import functools
# from aiocache import cached, Cache
# from aiocache.serializers import PickleSerializer
import sys
import requests
from typing import Any

from slackbot.parsing.slackapi import FileInfo, FileEvent

# Configure the logging level and format
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    stream=sys.stdout,
)


logger = logging.getLogger(__name__)


# Load environment variables from .env file
load_dotenv(find_dotenv())



# Set Slack API credentials
SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_SIGNING_SECRET = os.environ["SLACK_SIGNING_SECRET"]
SLACK_BOT_USER_ID = os.environ["SLACK_BOT_USER_ID"]

# Initialize the Slack app
app = AsyncApp(token=SLACK_BOT_TOKEN,
               signing_secret = SLACK_SIGNING_SECRET)




# Initialize the Flask app
api: FastAPI= FastAPI()



# def require_slack_verification(f):
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         if not await verify_slack_request():
#             abort(403)
#         return f(*args, **kwargs)

#     return decorated_function


# async def verify_slack_request(request:Request):
#     # Get the request headers
#     timestamp = request.headers.get("X-Slack-Request-Timestamp", "")
#     signature = request.headers.get("X-Slack-Signature", "")

#     # Check if the timestamp is within five minutes of the current time
#     current_timestamp = int(time.time())
#     if abs(current_timestamp - int(timestamp)) > 60 * 5:
#         raise HTTPException(status_code=403)

#     body=await request.body()
#     # Verify the request signature
#     if not signature_verifier.is_valid(
#         body=body.decode("utf-8"),
#         timestamp=timestamp,
#         signature=signature,
#     ):
#         raise HTTPException(status_code=403)

#@cached(
#    ttl=200, cache=Cache.MEMORY,  serializer=PickleSerializer())
@functools.lru_cache(maxsize=1)
async def cached_slack_client() -> AsyncWebClient:
     slack_client: AsyncWebClient = AsyncWebClient(token=os.environ["SLACK_BOT_TOKEN"])
     await slack_client.auth_test()
     return slack_client


# @cached(
#     ttl=200, cache=Cache.MEMORY,  serializer=PickleSerializer())
async def get_app_mention_for_file_info_id(file_info_id: str) -> str:
     raise ValueError(f" text for {file_info_id} Not in cache")

async def get_bot_user_id():
    """
    Get the bot user ID using the Slack API.
    Returns:
        str: The bot user ID.
    """
    try:
        # Initialize the Slack client with your bot token
        slack_client = await cached_slack_client()
        response = await slack_client.auth_test()
        return response["user_id"]
    except SlackApiError as e:
        print(f"Error: {e}")







@app.event("file_created")
async def handle_file_created(body, say):
    """ downloads the file transcribes it and sends it back to the user"""
    print(f"File Created:, I'll get right on that! {body=}")
    logger.warn(f"File Created:, I'll get right on that! {body=}")


@app.event("file_change")
async def handle_file_changed(body, say) -> None:
    """
    Event listener for file changes in Slack.
    When a file is updated, this function checks if the transcription status has changed.
    Args:
        body (dict): The event data received from Slack.
        say (callable): A function for sending a response to the channel.
    """
    # failes because of no channel id
    print(f"File Changed:, I'll get right on that! {body=}")
    logger.warn(f"File Changed:, I'll get right on that! {body=}")
    file_event: FileEvent = FileEvent(**body["event"])
    file_info: FileInfo = file_event.file_info(cached_slack_client())
    logger.warn(f"File Changed: Calling with {file_info=}")
    logger.warn(f"File Changed: File Info {file_info}")
    await say(f"File Changed: {file_info=}", channel=file_info.channels[0])

   
    

    

@app.event("app_mention")
async def handle_mentions(body, say):
    """
    Event listener for mentions in Slack.
    When the bot is mentioned, this function processes the text and sends a response.

    Args:
        body (dict): The event data received from Slack.
        say (callable): A function for sending a response to the channel.
    """
    logging.info(body)
    text = body["event"]["text"]
    mention = f"<@{SLACK_BOT_USER_ID}>"
    text = text.replace(mention, "").strip()
    logging.info("Received text: " + text.replace("\n", " "))

    await say("Sure, I'll get right on that!")
    await say(f"{body=}")
    response = draft_email(text)
    logging.info("Generated response: " + response.replace("\n", " "))
    await say(response)
    await say(body)

@api.get("/")
async def root(req: Request):
    client = await cached_slack_client()
    response = await client.chat_postMessage(
        channel='#admin',
        text="Hello world!")
    return Response(status_code=200, content="OK")

# Demo

@api.post("/slack/events")
async def slack_events(request: Request):
    logging.warn(f"Request {str(request)}")
    client = await cached_slack_client()
    handler = AsyncSlackRequestHandler(app)
    response = await client.chat_postMessage(
        channel='#admin',
        text="Hello world!")
    return await handler.handle(request)

#https://api.slack.com/types/file#authentication
#https://slackbotwebapp.azurewebsites.net/slack/events
# Run the fastapi app
if __name__ == "__main__":
    import uvicorn
    logging.info("Fast API app started")
    uvicorn.run("slackbot.app:api", host="0.0.0.0", port=8000, reload=True)



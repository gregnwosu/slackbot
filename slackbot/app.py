
from slackbot.parsing.slackapi import FileEvent, FileInfo, AppMentionEvent
from slack_bolt.adapter.starlette.async_handler import to_async_bolt_request
import os
from slack_sdk import WebClient
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.errors import SlackApiError
from slack_sdk.signature import SignatureVerifier
from fastapi import FastAPI, Request
from starlette.responses import Response
from slack_bolt import App
from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.fastapi.async_handler import AsyncSlackRequestHandler
from slack_bolt.adapter.fastapi import SlackRequestHandler
from fastapi import FastAPI, Request, HTTPException, Response
import slack_bolt
from dotenv import find_dotenv, load_dotenv
from fastapi import status
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

from slack_bolt.authorization import AuthorizeResult
async def authorize():
    return AuthorizeResult()
# Initialize the Slack app
app = AsyncApp(token=SLACK_BOT_TOKEN,
               signing_secret = SLACK_SIGNING_SECRET)
handler: AsyncSlackRequestHandler = AsyncSlackRequestHandler(app)

# Initialize the Flask app
api: FastAPI= FastAPI()

from slack_bolt.adapter.starlette.async_handler import to_async_bolt_request
#@require_slack_verification
@api.post("/slack/events")
async def slack_events(request: Request):
    return await handler.handle(request)


def require_slack_verification(f):
    @wraps(f)
    async def decorated_function(*args, **kwargs):
        if not await verify_slack_request(f):
            abort(403)
        return f(*args, **kwargs)

    return decorated_function

signature_verifier = SignatureVerifier(SLACK_SIGNING_SECRET)


async def verify_slack_request(request:Request):
    # Get the request headers
    timestamp = request.headers.get("X-Slack-Request-Timestamp", "")
    signature = request.headers.get("X-Slack-Signature", "")

    # Check if the timestamp is within five minutes of the current time
    current_timestamp = int(time.time())
    if abs(current_timestamp - int(timestamp)) > 60 * 5:
        raise HTTPException(status_code=403)

    body= await request.body()
    # Verify the request signature
    if not signature_verifier.is_valid(
        body=body.decode("utf-8"),
        timestamp=timestamp,
        signature=signature,
    ):
        raise HTTPException(status_code=403)

@functools.lru_cache(maxsize=1)
def cached_slack_client() -> AsyncWebClient:
     slack_client: AsyncWebClient = AsyncWebClient(token=os.environ["SLACK_BOT_TOKEN"])
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

# the response object looks like this, in particular the message object which contains the text sent to the client using the slack_client 

# response - status: 200, headers: {'Date': 'Thu, 22 Jun 2023 02:38:41 GMT', 'Server': 'Apache', 'Vary': 'Accept-Encoding', 
# 'x-slack-req-id': '75ed13eb554465e91d733edc789c8bc8', 'x-content-type-options': 'nosniff', 'x-xss-protection': '0', 
# 'Pragma': 'no-cache', 'Cache-Control': 'private, no-cache, no-store, must-revalidate', 'Expires': 'Sat, 26 Jul 1997 05:00:00 GMT', 
# 'Content-Type': 'application/json; charset=utf-8', 'x-accepted-oauth-scopes': 'chat:write', 
# 'x-oauth-scopes': 'app_mentions:read,chat:write,channels:history,files:read', 'Access-Control-Expose-Headers': 'x-slack-req-id, retry-after', 
# 'Access-Control-Allow-Headers': 'slack-route, x-slack-version-ts, x-b3-traceid, x-b3-spanid, x-b3-parentspanid, x-b3-sampled, x-b3-flags', 
# 'strict-transport-security': 'max-age=31536000; includeSubDomains; preload', 'x-slack-unique-id': 'ZJO0MXFSEqmPktRE0SIaGgAAECk',
#  'x-slack-backend': 'r', 'referrer-policy': 'no-referrer', 'Access-Control-Allow-Origin': '*', 
# 'Via': '1.1 slack-prod.tinyspeck.com, envoy-www-iad-uiodeehv, envoy-edge-lhr-bfidxpvw', 'Content-Encoding': 'gzip', 
# 'Content-Length': '394', 'x-envoy-upstream-service-time': '139', 'x-backend': 'main_normal main_canary_with_overflow main_control_with_overflow', 
# #'x-server': 'slack-www-hhvm-main-iad-elqy', 'x-slack-shared-secret-outcome': 'no-match', 'x-edge-backend': 'envoy-www', 
# 'x-slack-edge-shared-secret-outcome': 'no-match'}, body: {'ok': True, 'channel': 'C0595A85N4R', 'ts': '1687401521.384039', 
# 'message': {'bot_id': 'B058PNZL02H', 'type': 'message', 'text': 'Hello minnie tsts', 'user': 'U058V6AG10C', 'ts': '1687401521.384039',
#  'app_id': 'A058SM2MXS6', 'blocks': [{'type': 'rich_text', 'block_id': 'R+X', 'elements': [{'type': 'rich_text_section', 
# 'elements': [{'type': 'text', 'text': 'Hello minnie tsts'}]}]}], 'team': 'T058PNE2HKP', 
# 'bot_profile': {'id': 'B058PNZL02H', 'app_id': 'A058SM2MXS6', 'name': 'Aria', 
# 'icons': {'image_36': 'https://avatars.slack-edge.com/2023-05-21/5298593448691_15a7452d31fcaafd5a9d_36.jpg',
#  'image_48': 'https://avatars.slack-edge.com/2023-05-21/5298593448691_15a7452d31fcaafd5a9d_48.jpg', 
# 'image_72': 'https://avatars.slack-edge.com/2023-05-21/5298593448691_15a7452d31fcaafd5a9d_72.jpg'}, 
# 'deleted': False, 'updated': 1684712126, 'team_id': 'T058PNE2HKP'}}}

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
    file_info: FileInfo = await file_event.file_info(cached_slack_client())
    logger.warn(f"File Changed: Calling with {file_info=}")
    logger.warn(f"File Changed: File Info {file_info}")
    await say(f"File Changed: {file_info=}", channel=file_info.channels[0]) 

from  slack_bolt.request.async_request import AsyncBoltRequest
@app.event("app_mention")
async def handle_mentions(body: dict, say):
    """
    Event listener for mentions in Slack.
    When the bot is mentioned, this function processes the text and sends a response.

    Args:
        body (dict): The event data received from Slack.
        say (callable): A function for sending a response to the channel.



    """
    model = AppMentionEvent(**body['event'])
    client = cached_slack_client()
    text = body["event"]["text"]
    mention = f"<@{SLACK_BOT_USER_ID}>"
    text = text.replace(mention, "").strip()
    logging.debug(f"{type(model)=}")
    logging.debug("Received text: " + text.replace("\n", " "))

    await say("Sure, I'll get right on that!")
    await say(f"{body=}")
    #huh = draft_email(text)
    huh = "minnie"
    await client.chat_postMessage(
        channel='#admin',
        text=f"Hello {huh} tsts")
    return Response(status_code=200, content="OKieDokie")
    
    
@api.get("/")
async def root(req: Request):
    client = cached_slack_client()
    await client.chat_postMessage(
        channel='#admin',
        text="Hello world!")
    
    return Response(status_code=200, content="OK")


    

#https://api.slack.com/types/file#authentication
#https://slackbotwebapp.azurewebsites.net/slack/events
# Run the fastapi app
if __name__ == "__main__":
    import uvicorn
    logging.info("Fast API app started")
    uvicorn.run("slackbot.app:api", host="0.0.0.0", port=8000, reload=True)



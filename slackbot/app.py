import datetime as dt
import functools
import logging
import os
import sys
import time

import aioredis
import requests
from aiocache import cached
from dotenv import find_dotenv, load_dotenv
from fastapi import FastAPI, HTTPException, Request
from slack_bolt.adapter.fastapi.async_handler import AsyncSlackRequestHandler
from slack_bolt.async_app import AsyncApp
from slack_bolt.authorization import AuthorizeResult
from slack_sdk.errors import SlackApiError
from slack_sdk.signature import SignatureVerifier
from slack_sdk.web.async_client import AsyncWebClient
from starlette.responses import Response

from slackbot import agent
from slackbot.parsing.appmention.event import AppMentionEvent
# from slackbot import speak
# from slackbot.instruct import user_proxy_assistant
# from slackbot.instruct.user_proxy_assistant import _client as client, SendMessage
# from slackbot.instruct.utils import get_completion
# from aiocache.serializers import PickleSerializer
from slackbot.parsing.file.event import FileEvent, FileInfo
from slackbot.parsing.file.model import MimeType
from slackbot.parsing.message.event import MessageSubType
from slackbot.utils import get_cache

# Configure the logging level and format
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    stream=sys.stdout,
)

logger = logging.getLogger(__name__)


class BearerAuth(requests.auth.AuthBase):
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers["authorization"] = "Bearer " + self.token
        return r


# Load environment variables from .env file
load_dotenv(find_dotenv())

# Set Slack API credentials
SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_SIGNING_SECRET = os.environ["SLACK_SIGNING_SECRET"]
SLACK_BOT_USER_ID = os.environ["SLACK_BOT_USER_ID"]
REDIS_URL = os.environ["REDIS_URL"]
REDIS_KEY = os.environ["REDIS_KEY"]


async def authorize():
    return AuthorizeResult()


# Initialize the Slack app
app = AsyncApp(token=SLACK_BOT_TOKEN, signing_secret=SLACK_SIGNING_SECRET)
handler: AsyncSlackRequestHandler = AsyncSlackRequestHandler(app)

# Initialize the Flask app
api: FastAPI = FastAPI()


# @require_slack_verification
@api.post("/slack/events")
async def slack_events(request: Request):
    return await handler.handle(request)


# def require_slack_verification(f):
#     @wraps(f)
#     async def decorated_function(*args, **kwargs):
#         if not await verify_slack_request(f):
#             abort(403)
#         return f(*args, **kwargs)
#
#     return decorated_function


signature_verifier = SignatureVerifier(SLACK_SIGNING_SECRET)


async def verify_slack_request(request: Request):
    # Get the request headers
    timestamp = request.headers.get("X-Slack-Request-Timestamp", "")
    signature = request.headers.get("X-Slack-Signature", "")

    # Check if the timestamp is within five minutes of the current time
    current_timestamp = int(time.time())
    if abs(current_timestamp - int(timestamp)) > 60 * 5:
        raise HTTPException(status_code=403)

    body = await request.body()
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


@cached(ttl=60)
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


# TODO this should, read the speech if it is a sound file as a directive
# if it is any other type of file it should be considered data and  form part of the RAG vector store for the channel
@app.event("file_created")
async def handle_file_created(body, say):
    """downloads the file transcribes it and sends it back to the user"""
    print(f"File Created:, I'll get right on that! {body=}")
    logger.debug(f"File Created:, I'll get right on that! {body=}")


@app.event("file_shared")
async def handle_file_shared(body, say) -> None:
    return None


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
    file_event: FileEvent = FileEvent(**body["event"])
    file_info: FileInfo = await file_event.file_info(cached_slack_client())

    slack_channel = list(file_info.shares.public)[0] if file_info.shares else "C0595A85N4R"

    # transcription = await file_info.vtt_txt(SLACK_BOT_TOKEN)
    # if logger.isEnabledFor(logging.DEBUG):

    try:
        bot_cache: aioredis.Redis = get_cache()
        cached_text: str = await bot_cache.get(file_info.id)
        if not cached_text:
            keys = await bot_cache.keys()
            if logger.isEnabledFor(logging.DEBUG):
                await say(f"File Changed: Cache miss {keys=}", channel=slack_channel)

        else:
            if logger.isEnabledFor(logging.DEBUG):
                await say(f"File Changed: Cache hit {cached_text=}", channel=slack_channel)
        # slack_client: AsyncWebClient = cached_slack_client()
        # extra_info = f", extra info is {cached_text}" if cached_text else ""
        # ai_request = f"hi please service this request: \n {transcription}  {extra_info}"
        # thread = client.beta.threads.create()

        # response = await get_completion(user_message, user_proxy, user_proxy_tools, thread)
        #
        # audio_bytes = await speak.text_to_speech(response)
        #
        # speech_upload_response = await slack_client.files_upload(
        #     channels=[slack_channel],
        #     file=audio_bytes,
        #     filename="audio.mp3",
        #     initial_comment=response,
        #     filetype=MimeType.AUDIO_MP3.value,
        # )
        return None
    except Exception as e:
        await say(f"Error {e=}", channel="C0595A85N4R")
        raise e
    finally:
        await bot_cache.close()


@app.event("message")
async def handle_message(body: dict, say):
    """
    Event listener for mentions in Slack.
    When the bot is mentioned, this function processes the text and sends a response.
    Args:
        body (dict): The event data received from Slack.
        say (callable): A function for sending a response to the channel.
    """

    event = body["event"]

    if sub_type := event.get("subtype", None):
        model = MessageSubType[sub_type].value(**event)
    else:
        model = MessageSubType.message.value(**event)

    text = body["event"]["text"]
    mention = f"<@{SLACK_BOT_USER_ID}>"
    text = text.replace(mention, "").strip()

    await say("Message event, I'll get right on that!")

    if isinstance(model, MessageSubType.file_share.value):
        for fileinfo in model.files:
            if fileinfo.mimetype in [
                MimeType.AUDIO_WEBM.value,
                MimeType.AUDIO_MP4.value,
            ]:
                say(f"************getting cache for text {fileinfo.id=} {text=}")
                try:
                    text_cache: aioredis.Redis = get_cache()
                    if logger.isEnabledFor(logging.DEBUG):
                        await say(f"*************caching key and  values {fileinfo.id=} {text=} {text_cache=}")
                    await text_cache.set(fileinfo.id, text, ex=dt.timedelta(minutes=5))
                    # cache the text for the file
                    keys = await text_cache.keys()
                    if logger.isEnabledFor(logging.DEBUG):
                        await say(f"cache keys {keys=}")
                        await say(
                            f"Need to wait for audio to be transcribed for  {fileinfo}",
                            channel=model.channel,
                        )
                except Exception as e:
                    await say(f"Error {e=}")
                    raise e
                finally:

                    await text_cache.close()

    return model


@app.event("app_mention")
async def handle_mentions(body: dict, say):
    """
    Event listener for mentions in Slack.
    When the bot is mentioned, this function processes the text and sends a response.
    Args:
        body (dict): The event data received from Slack.
        say (callable): A function for sending a response to the channel.
    """
    from agency_swarm.messages import MessageOutput
    model = AppMentionEvent(**body["event"])
    client = cached_slack_client()
    text = body["event"]["text"]
    mention = f"<@{SLACK_BOT_USER_ID}>"
    text = text.replace(mention, "").strip()
    prompt = f"Slack Channel: {model.channel} \n Slack User: {model.user} \n Agency Please Respond The Following Text: {text}"
    await say("got your message sending it to the agent swarm", channel=model.channel)
    conversation = agent.agency.get_completion(prompt)
    msg_output = next(conversation)
    await say(msg_output.content, channel=model.channel)
    return Response(status_code=200, content="OKieDokie")


@api.get("/")
async def root(req: Request):
    client = cached_slack_client()
    cache = await get_cache()
    await cache.flushall()
    return Response(status_code=200, content="OK")


# https://api.slack.com/types/file#authentication
# https://slackbotwebapp.azurewebsites.net/slack/events
# Run the fastapi app
if __name__ == "__main__":
    import uvicorn
    logging.info("Fast API app started")
    uvicorn.run("slackbot.app:api", host="0.0.0.0", port=8000, reload=True)

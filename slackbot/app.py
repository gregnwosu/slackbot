import sys
import os
import datetime as dt
import pickle
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

# from aiocache.serializers import PickleSerializer
from slackbot.parsing.file.event import FileInfo, FileEvent
from slackbot.parsing.file.model import MimeType
from slackbot.parsing.message.event import MessageSubType
import slackbot.functions as functions
from slackbot.tools import Conversation

# Configure the logging level and format
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    stream=sys.stdout,
)
import pickle

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


def get_cache() -> aioredis.Redis:
    return aioredis.Redis(
        host=REDIS_URL,
        password=REDIS_KEY,
        ssl=True,
        port=6380,
        db=0,
        decode_responses=True,
    )


# cachetools.TTLCache(maxsize=100, ttl=300)


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


def require_slack_verification(f):
    @wraps(f)
    async def decorated_function(*args, **kwargs):
        if not await verify_slack_request(f):
            abort(403)
        return f(*args, **kwargs)

    return decorated_function


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


@app.event("file_created")
async def handle_file_created(body, say):
    """downloads the file transcribes it and sends it back to the user"""
    print(f"File Created:, I'll get right on that! {body=}")
    logger.debug(f"File Created:, I'll get right on that! {body=}")


@app.event("file_shared")
async def handle_file_shared(body, say) -> None:
    return None


async def get_memory_for_channel(channel_id: str) -> ConversationSummaryBufferMemory:
    async with get_cache() as channel_memory_cache:
        channel_data = channel_memory_cache.get(f"memory:{channel_id}")
        if not channel_data:
            channel_data = pickle.dumps(
                ConversationSummaryBufferMemory(llm=OpenAI(model_name="gpt-4"))
            )
            channel_memory_cache.set(
                f"memory:{channel_id}", channel_data, ex=dt.timedelta(hours=5)
            )
        return pickle.loads(channel_data)



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

    channel = list(file_info.shares.public)[0] if file_info.shares else "C0595A85N4R"

    transcription = await file_info.vtt_txt(SLACK_BOT_TOKEN)
    # if logger.isEnabledFor(logging.DEBUG):

    try:
        bot_cache: aioredis.Redis = get_cache()
        cached_text: str = await bot_cache.get(file_info.id)
        if not cached_text:
            keys = await bot_cache.keys()
            if logger.isEnabledFor(logging.DEBUG):
                await say(f"File Changed: Cache miss {keys=}", channel=channel)

        else:
            if logger.isEnabledFor(logging.DEBUG):
                await say(f"File Changed: Cache hit {cached_text=}", channel=channel)
        slack_client: AsyncWebClient = cached_slack_client()
        extra_info = f", extra info is {cached_text}" if cached_text else ""
        ai_request = f"hi please service this request: \n {transcription}  {extra_info}"

        channel_memory = await get_memory_for_channel(channel)
        convo = Conversation(
            agent=None, level=3, memory=channel_memory, channel=channel
        )
        ai_answer = await convo.ask(
            agent=Agents.Aria,
            input_question=ai_request,
            level=2,
            channel=convo.channel,
            memory=convo.memory,
        )

        audio_bytes = await functions.generate_audio(ai_answer, bot_cache)

        response = await slack_client.files_upload(
            channels=[channel],
            file=audio_bytes,
            filename="audio.mp3",
            initial_comment=ai_answer,
            filetype=MimeType.AUDIO_MP3.value,
        )
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
                        await say(
                            f"*************caching key and  values {fileinfo.id=} {text=} {text_cache=}"
                        )
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

    model = AppMentionEvent(**body["event"])
    client = cached_slack_client()
    text = body["event"]["text"]
    mention = f"<@{SLACK_BOT_USER_ID}>"
    text = text.replace(mention, "").strip()
    logging.debug(f"{type(model)=}")
    logging.debug("Received text: " + text.replace("\n", " "))

    await say("Sure, I'll get right on that!")

    # await client.chat_postMessage(
    #     channel='#admin',
    #     text="Hello  tsts")
    return Response(status_code=200, content="OKieDokie")


@api.get("/")
async def root(req: Request):
    client = cached_slack_client()
    # await client.chat_postMessage(
    #     channel='#admin',
    #     text="Hello world!")
    return Response(status_code=200, content="OK")


# https://api.slack.com/types/file#authentication
# https://slackbotwebapp.azurewebsites.net/slack/events
# Run the fastapi app
if __name__ == "__main__":
    import uvicorn

    logging.info("Fast API app started")
    uvicorn.run("slackbot.app:api", host="0.0.0.0", port=8000, reload=True)

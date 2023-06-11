
from slackbot.parsing.slackapi import FileEvent, FileInfo
import os
from slack_sdk import WebClient
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.errors import SlackApiError
from slack_sdk.signature import SignatureVerifier
from slack_bolt.adapter.flask import SlackRequestHandler
from slack_bolt import App
import slack_bolt
from dotenv import find_dotenv, load_dotenv
from flask import Flask, request, abort
from functions import draft_email
import logging
from functools import lru_cache, wraps
import time
import asyncio
import functools
from aiocache import cached, Cache
from aiocache.serializers import PickleSerializer
import sys
import requests

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
slack_app = slack_bolt.App(token=SLACK_BOT_TOKEN)
signature_verifier = SignatureVerifier(SLACK_SIGNING_SECRET)

# Initialize the Flask app
flask_app = Flask(__name__)
flask_app.logger.setLevel(logging.INFO)
handler = SlackRequestHandler(slack_app)


def require_slack_verification(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not verify_slack_request():
            abort(403)
        return f(*args, **kwargs)

    return decorated_function


def verify_slack_request():
    # Get the request headers
    timestamp = request.headers.get("X-Slack-Request-Timestamp", "")
    signature = request.headers.get("X-Slack-Signature", "")

    # Check if the timestamp is within five minutes of the current time
    current_timestamp = int(time.time())
    if abs(current_timestamp - int(timestamp)) > 60 * 5:
        return False

    # Verify the request signature
    return signature_verifier.is_valid(
        body=request.get_data().decode("utf-8"),
        timestamp=timestamp,
        signature=signature,
    )

@cached(
    ttl=200, cache=Cache.MEMORY,  serializer=PickleSerializer())
async def cached_slack_client() -> AsyncWebClient:
     slack_client: AsyncWebClient = AsyncWebClient(token=os.environ["SLACK_BOT_TOKEN"])
     await slack_client.auth_test()
     return slack_client


@cached(
    ttl=200, cache=Cache.MEMORY,  serializer=PickleSerializer())
async def get_app_mention_for_file_info_id(file_info_id: str) -> str:
     raise ValueError(f" text for {file_info_id} Not in cache")

def get_bot_user_id():
    """
    Get the bot user ID using the Slack API.
    Returns:
        str: The bot user ID.
    """
    try:
        # Initialize the Slack client with your bot token
        slack_client = cached_slack_client()
        response = slack_client.auth_test()
        return response["user_id"]
    except SlackApiError as e:
        print(f"Error: {e}")


def my_function(text):
    """
    Custom function to process the text and return a response.
    In this example, the function converts the input text to uppercase.

    Args:
        text (str): The input text to process.

    Returns:
        str: The processed text.
    """
    return text.upper()




@slack_app.event("file_created")
async def handle_file_created(body, say):
    """ downloads the file transcribes it and sends it back to the user"""
    print(f"File Created:, I'll get right on that! {body=}")
    logger.warn(f"File Created:, I'll get right on that! {body=}")


@slack_app.event("file_change")
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
    say(f"File Changed: {file_info=}", channel=file_info.channels[0])

   
    

    

@slack_app.event("app_mention")
async def handle_mentions(body, say):
    """
    Event listener for mentions in Slack.
    When the bot is mentioned, this function processes the text and sends a response.

    Args:
        body (dict): The event data received from Slack.
        say (callable): A function for sending a response to the channel.
    """
    text = body["event"]["text"]
    logging.info(body)
    mention = f"<@{SLACK_BOT_USER_ID}>"
    text = text.replace(mention, "").strip()
    logging.info("Received text: " + text.replace("\n", " "))

    say("Sure, I'll get right on that!")
    say(f"{body=}")
    response = draft_email(text)
    logging.info("Generated response: " + response.replace("\n", " "))
    say(response)
    say(body)


# Demo
@flask_app.route("/slack/events", methods=["POST"])
@require_slack_verification
def slack_events():
    """
    Route for handling Slack events.
    This function passes the incoming HTTP request to the SlackRequestHandler for processing.

    Returns:
        Response: The result of handling the request.
    """

    return handler.handle(request)
#https://api.slack.com/types/file#authentication

# Run the Flask app
if __name__ == "__main__":
    logging.info("Flask app started")
    flask_app.run(host="0.0.0.0", port=8000)



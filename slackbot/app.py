import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_sdk.signature import SignatureVerifier
from slack_bolt.adapter.flask import SlackRequestHandler
from slack_bolt import App
from dotenv import find_dotenv, load_dotenv
from flask import Flask, request, abort
from functions import draft_email
import logging
from functools import lru_cache, wraps
import time
import sys

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
app = App(token=SLACK_BOT_TOKEN)
signature_verifier = SignatureVerifier(SLACK_SIGNING_SECRET)

# Initialize the Flask app
flask_app = Flask(__name__)
flask_app.logger.setLevel(logging.INFO)
handler = SlackRequestHandler(app)


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

@lru_cache(maxsize=1)
def cached_slack_client():
     slack_client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
     slack_client.auth_test()
     return slack_client

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




@app.event("file_created")
def handle_file_created(body, say):
    """ downloads the file transcribes it and sends it back to the user"""
    print(f"File Created:, I'll get right on that! {body=}")
    logger.warn(f"File Created:, I'll get right on that! {body=}")



# @app.event("file_shared")
# def handle_file_shared(body, say):
#     """ downloads the file transcribes it and sends it back to the user"""
#     print(f"File Shared:, I'll get right on that! {body=}")
#     logger.warning(f"File Shared:, I'll get right on that! {body=}")
    
#     file_id = body["event"]['file_id']
#     channel_id = body["event"]['channel_id']
#     slack_client = cached_slack_client()
#     logger.warn(f"File Shared: Calling with {channel_id=}")
#     logger.warn(f"File Shared: Calling with {file_id=}")
#     file_info = slack_client.files_info(file=file_id)
#     logger.warn(f"File Shared: File Info {file_info}")
#     #say(channel=channel_id, text=f"File Shared: {file_info}")
#     #print(f"File Transcription status is : {file_info.transcription=}")
#     #logger.warn(f"File Transcription status is : {file_info.transcription=}")

    
from slackbot.parsing.slackapi import FileEvent, FileInfo
@app.event("file_change")
def handle_file_changed(body, say):
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
    say(f"File Changed: {file_info.transcription=}", channel=file_info.channel_id)

   
    

    

@app.event("app_mention")
def handle_mentions(body, say):
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
    # response = my_function(text)
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



{'token': 'waNounRnAWVeA53FlYyaPaP8', 'team_id': 'T058PNE2HKP', 'api_app_id': 'A058SM2MXS6', 'event': {'type': 'app_mention', 'text': '<@U058V6AG10C>', 'files': [{'id': 'F05B218U5FZ', 'created': 1686168176, 'timestamp': 1686168176, 'name': 'audio_message.webm', 'title': 'audio_message.webm', 'mimetype': 'audio/webm', 'filetype': 'webm', 'pretty_type': 'WebM', 'user': 'U058V5QTW12', 'user_team': 'T058PNE2HKP', 'editable': False, 'size': 51648, 'mode': 'hosted', 'is_external': False, 'external_type': '', 'is_public': True, 'public_url_shared': False, 'display_as_bot': False, 'username': '', 'subtype': 'slack_audio', 'transcription': {'status': 'processing'}, 'url_private': 'https://files.slack.com/files-tmb/T058PNE2HKP-F05B218U5FZ-4be882953e/audio_message_audio.mp4', 'url_private_download': 'https://files.slack.com/files-tmb/T058PNE2HKP-F05B218U5FZ-4be882953e/download/audio_message_audio.mp4', 'duration_ms': 3177, 'aac': 'https://files.slack.com/files-tmb/T058PNE2HKP-F05B218U5FZ-4be882953e/audio_message_audio.mp4', 'audio_wave_samples': [32, 18, 6, 4, 5, 8, 9, 6, 3, 2, 6, 46, 61, 73, 82, 82, 86, 88, 90, 91, 88, 90, 90, 86, 86, 85, 85, 80, 87, 96, 82, 84, 93, 91, 96, 92, 93, 76, 80, 76, 90, 78, 93, 91, 100, 88, 100, 94, 95, 85, 93, 88, 96, 99, 99, 98, 90, 88, 100, 91, 82, 71, 79, 90, 95, 88, 76, 87, 99, 99, 89, 97, 93, 98, 76, 73, 75, 87, 65, 43, 83, 98, 87, 66, 66, 72, 62, 53, 56, 43, 27, 28, 22, 22, 26, 27, 19, 15, 21, 32], 'media_display_type': 'audio', 'permalink': 'https://ai-experimentshq.slack.com/files/U058V5QTW12/F05B218U5FZ/audio_message.webm', 'permalink_public': 'https://slack-files.com/T058PNE2HKP-F05B218U5FZ-7bd65ed9f0', 'is_starred': False, 'has_rich_preview': False, 'file_access': 'visible'}], 'upload': False, 'user': 'U058V5QTW12', 'display_as_bot': False, 'ts': '1686168182.722449', 'blocks': [{'type': 'rich_text', 'block_id': 'ESK+', 'elements': [{'type': 'rich_text_section', 'elements': [{'type': 'user', 'user_id': 'U058V6AG10C'}]}]}], 'client_msg_id': 'b15dd83d-b33b-4f18-a25e-3b0650a92d9f', 'channel': 'C0595A85N4R', 'event_ts': '1686168182.722449'}, 'type': 'event_callback', 'event_id': 'Ev05C68EUN1E', 'event_time': 1686168182, 'authorizations': [{'enterprise_id': None, 'team_id': 'T058PNE2HKP', 'user_id': 'U058V6AG10C', 'is_bot': True, 'is_enterprise_install': False}], 'is_ext_shared_channel': False, 'event_context': '4-eyJldCI6ImFwcF9tZW50aW9uIiwidGlkIjoiVDA1OFBORTJIS1AiLCJhaWQiOiJBMDU4U00yTVhTNiIsImNpZCI6IkMwNTk1QTg1TjRSIn0'}
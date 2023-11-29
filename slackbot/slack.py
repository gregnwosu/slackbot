import os
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.web.client import WebClient
from agency_swarm.tools import BaseTool
from pydantic import Field

client: WebClient = Field(default=WebClient(token=os.environ['SLACK_API_TOKEN']),
                               description="The Slack client used to send text messages to the user.")


class SlackTexter(BaseTool):
    """
    This tool enables an agent to communicate with a user through Slack a slack text message.
    It is best used when the information lengthy or technical and not easily conveyed through speech.
    """

    channel: str = Field(default="#admin",
                         description="The Slack channel used to send text messages to the user. Messages should only be sent to the relevant channel.")
    text: str = Field(default="The message to send to the user.",
                      description="The text message to send to the user.")

    def run(self):
        # Your custom tool logic goes here
        response = client.chat_postMessage(
            channel=self.channel,
            text=self.text)
        return "message sent" if response["ok"] else f"message not sent: response was {response}"


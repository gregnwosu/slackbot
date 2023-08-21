import os
from dataclasses import dataclass
from enum import Enum
from typing import List

from slack_sdk.web.async_client import AsyncWebClient

from slackbot.llm import LLM
from slackbot.prompts import PromptTemplates


@dataclass
class Agent:
    display_name: str
    model: LLM
    prompt_template: str
    tool_names: List[str]
    slack_client: AsyncWebClient


class Agents(Enum):
    Aria = Agent(
        "Aria",
        LLM.GPT4.value,
        PromptTemplates.Aria.value,
        ["Aria"],#  "Geoffrey", ],#"Speak", "SearchBing", "Gorilla",],
        AsyncWebClient(token=os.environ["SLACK_BOT_TOKEN"]),
    )
    Gorilla = Agent(
        "Gorilla",
        LLM.Gorilla.value,
        PromptTemplates.Gorilla.value,
        ["SearchBing", "Geoffrey"],
        AsyncWebClient(token=os.environ["SLACK_BOT_TOKEN"]),
    )
    Geoffrey = Agent(
        "Geoffrey",
        LLM.GPT4.value,
        PromptTemplates.Geoffrey.value,
        ["SearchBing"],# "Gorilla"],
        AsyncWebClient(token=os.environ["SLACK_BOT_TOKEN"]),
    )

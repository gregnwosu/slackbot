from enum import Enum
from functools import partial
from typing import Callable, List, Optional, Union
from tenacity import retry, stop_after_attempt
from langchain.agents import initialize_agent, Tool
from langchain.agents import AgentType
from langchain.memory import ConversationSummaryBufferMemory
from slackbot.agent import Agents
from slackbot.search import search_bing
from slackbot.speak import speak
from dataclasses import dataclass
from langchain.chat_models import ChatOpenAI
import openai
import os
from dotenv import load_dotenv, find_dotenv
from slackbot.gorilla import get_gorilla_response


load_dotenv(find_dotenv())




@dataclass(frozen=True)
class ToolDetails:
    name: str
    description: str
    coroutine: Optional[Callable] = None


class Tools(Enum):
    Aria=ToolDetails(
                name="Aria",
                #partially initialise so just input is needed
                coroutine=None,
                description="Adria is a language model that can answer questions and generate text. She is aware of all of the other agents and their capabilities. Which she can use as tools in order to decompose , delegate and recompose a problem into a solution.",
            )
    Gorilla=ToolDetails(
                name="Gorilla",
                coroutine=get_gorilla_response,
                description="ONLY USE THIS TOOL TO GENERATE CODE FOR Specific Scientifc, Legal, Physics, Questions. Gorilla should not be used to answer general knowledge questions, instead Ask Geoffrey or Aria or BingSearch.",
            )
    Geoffrey=ToolDetails(
                name="Geoffrey",
                coroutine=None,
                description="Geoffrey is an intelligent general language model that can perform complex reasoning and solve intridcate logical problems. He is best used when the problem is too complex for Aria to solve on her own and doesnt require expert knowledge.")
    SearchBing =ToolDetails(
                name="SearchBing",
                description="This tool will search the internet for the answer to your question. It is best used when the problem requires the most up to date information, api defintion or publicshed context.",
                coroutine=search_bing)
    Speak = ToolDetails(
        name="Speak",
        description="Use this tool if you make a discovery that you feel should be reported to the original questioner. This tool will convert text to speech and post it to the designated channel as if it was said by Aria",
        coroutine=speak)

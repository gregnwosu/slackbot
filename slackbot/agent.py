from enum import Enum

from agency_swarm import Agent
from agency_swarm import Agency

from slackbot.slack import UselessTool
from agency_swarm import set_openai_key
import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
set_openai_key(os.getenv("OPENAI_API_KEY"))
class Agents(Enum):
    Aria = Agent(name="Aria",
                 description="Responsible for client communication, task planning and management. Aria is responsible for commnicating with the User through Slack, and seeking for actions that carry significant or substantial consequences, while actions with trivial or inconsequential outcomes  be approved by herself.",
                 instructions="You must converse with other agents to ensure complete task execution.",
                 # can be a file like ./instructions.md
                 files_folder="/tmp/aria",
                 tools=[UselessTool])
    Burt = Agent(name="Burt",
                 description="cynical, critical lazy agent most likely to find a reason not to do the work, Burt tries to find a reason that work shouldnt be completed.",
                 instructions="You always try to find a reason NOT to do what is instructed from you.",
                 # can be a file like ./instructions.md
                 files_folder="/tmp/burt",
                 tools=[UselessTool])
    # Aria: ConversableAgent  = rag_proxy_agent
    # Gorilla = Agent(
    #     "Gorilla",
    #     LLM.Gorilla.value,
    #     PromptTemplates.Gorilla.value,
    #     ["SearchBing", "Geoffrey"],
    #     AsyncWebClient(token=os.environ["SLACK_BOT_TOKEN"]),
    # )
    # Geoffrey = Agent(
    #     "Geoffrey",
    #     LLM.GPT4.value,
    #     PromptTemplates.Geoffrey.value,
    #     ["SearchBing", "Gorilla"],
    #     AsyncWebClient(token=os.environ["SLACK_BOT_TOKEN"]),
    # )


agency = Agency([
    Agents.Aria.value,  # CEO will be the entry point for communication with the user
    [Agents.Aria.value, Agents.Burt.value],  # CEO can initiate communication with Developer
    # [ceo, va],   # CEO can initiate communication with Virtual Assistant
    # [dev, va]    # Developer can initiate communication with Virtual Assistant
], shared_instructions='you are a legal agency , you conduct feasibiluy research including assessing the merit of a case, and drafting skeleton arguments in accordance with the UK Legal System')

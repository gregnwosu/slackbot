from enum import Enum

from agency_swarm import Agent
from agency_swarm import Agency

from slackbot.slack import SlackTexter


class Agents(Enum):
    Aria = Agent(name="Aria",
                 description="Responsible for client communication, task planning and management. Aria is responsible for commnicating with the User through Slack, and seeking for actions that carry significant or substantial consequences, while actions with trivial or inconsequential outcomes  be approved by herself.",
                 instructions="You must converse with other agents to ensure complete task execution.",
                 # can be a file like ./instructions.md
                 files_folder=None,
                 tools=[SlackTexter])
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
    # [ceo, dev],  # CEO can initiate communication with Developer
    # [ceo, va],   # CEO can initiate communication with Virtual Assistant
    # [dev, va]    # Developer can initiate communication with Virtual Assistant
])

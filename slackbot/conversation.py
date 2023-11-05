from dataclasses import dataclass
from functools import partial
from typing import List, Optional

from autogen.agentchat.conversable_agent import ConversableAgent

from slackbot import utils
from slackbot.agent import Agents
from slackbot.tools import Tools


def not_implemented(input_question: str):
    raise NotImplementedError(
        f"This function is not implemented yet. {input_question=}"
    )


@dataclass
class Conversation:
    agents: list[ConversableAgent]
    channel: str
    
    @utils.redis_memory_decorator
    # @retry(stop=stop_after_attempt(3))
    async def ask(
        self,
        input_question: str,
        channel: str,
        agent: Agents = Agents.Aria,
    ) -> str:
        # we always aria (the proxy agent) to ask the agent the question
        return await Agents.Aria.value.a_initiate_chat(agent.value, problem=input_question)


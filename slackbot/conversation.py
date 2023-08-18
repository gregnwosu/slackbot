from dataclasses import dataclass
from functools import partial
from typing import List, Optional

from langchain.agents import AgentType, Tool, initialize_agent
from langchain.memory import ConversationSummaryBufferMemory

from slackbot import utils
from slackbot.agent import Agents
from slackbot.tools import Tools


def not_implemented(input_question: str):
    raise NotImplementedError(
        f"This function is not implemented yet. {input_question=}"
    )


@dataclass
class Conversation:
    agent: Optional[Agents]
    level: int
    memory: ConversationSummaryBufferMemory
    channel: str

    @utils.redis_memory_decorator
    # @retry(stop=stop_after_attempt(3))
    async def ask(
        self,
        input_question: str,
        level: int,
        memory: ConversationSummaryBufferMemory,
        channel: str,
        agent: Agents = Agents.Aria,
    ) -> str:
        level = level - 1

        tools: List[Tool] = [
            Tool(
                name=Tools[nm].name,
                func=not_implemented,
                coroutine=partial(
                    Tools[nm].value.coroutine
                    if Tools[nm].value.coroutine
                    else self.ask,
                    memory=self.memory,
                    channel=channel,
                    agent=Agents[nm] if hasattr(Agents, nm) else Agents.Aria,
                    level=level,
                ),
                description=Tools[nm].value.description,
            )
            for nm in agent.value.tool_names
        ]
        tools_description = "\n\t".join(
            [f"{tool.name}:{tool.description}" for tool in tools]
        )
        initialised_agent = initialize_agent(
            tools,
            agent.value.model,
            agent=AgentType.OPENAI_MULTI_FUNCTIONS,
            verbose=True,
            memory=memory,
            prompt=agent.value.prompt_template,
        )
        if level > 0:
            answer = await initialised_agent.arun(
                input=agent.value.prompt_template.format(
                    input_question=input_question,
                    level=level,
                    tools_description=tools_description,
                )
            )
        else:
            answer = await initialised_agent.arun(
                input=f"please summarise the answer to the question: {input_question}. You may not call any functions or use any tools."
            )

        return answer

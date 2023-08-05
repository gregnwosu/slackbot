from slack_sdk.web.async_client import AsyncWebClient
from langchain.agents import initialize_agent, Tool
from langchain.agents import AgentType
from langchain.chat_models import ChatOpenAI

import os
from enum import Enum
from search import search_bing
from typing import Any
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain.chains import ConversationChain

from langchain import OpenAI

import os
from langchain.memory import ConversationSummaryBufferMemory
from dotenv import load_dotenv, find_dotenv
from tenacity import retry, stop_after_attempt

load_dotenv(find_dotenv())


SERPAPI_API_KEY = os.environ["SERPAPI_API_KEY"]




def make_function_async(func):
    async def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


class Agents(Enum):
    Aria = (
        "Aria",
        os.environ["SLACK_BOT_TOKEN"],
        ChatOpenAI(
            model_name="gpt-3.5-turbo",
            temperature=1,
            openai_api_key=os.environ["OPENAI_API_KEY"],
        ),
    )
    Daisuke = (
        "Daisuke",
        os.environ["SLACK_BOT_TOKEN"],
        ChatOpenAI(
            model_name="gpt-3.5-turbo",
            temperature=1,
            openai_api_key=os.environ["OPENAI_API_KEY"],
        ),
    )
    Geoffrey = (
        "Geoffrey",
        os.environ["SLACK_BOT_TOKEN"],
        ChatOpenAI(
            model_name="gpt-4",
            temperature=0,
            openai_api_key=os.environ["OPENAI_API_KEY"],
        ),
    )

    def __init__(self, name: str, slack_key: str, model: Any) -> None:
        super().__init__()
        # self.name = name
        self.slack_key = slack_key
        self.model = model
        self.slack_client: AsyncWebClient = AsyncWebClient(token=self.slack_key)

    def tools(self, level: int, memory=ConversationSummaryBufferMemory(llm=OpenAI())):
        if level < 1:
            return [Tool(
                name="Aria",
                func=Agents.Aria.make_ask(level=level, memory=memory),
                coroutine=Agents.Aria.make_ask(level=level, memory=memory),
                description="Adria is a language model that can answer questions and generate text. Shes fast friendly and mildy creative always ready to help",
            ),]
        return [
            # Tool(
            #     name="Search",
            #     func=SerpAPIWrapper(serpapi_api_key=os.environ["SERPAPI_API_KEY"]).run,
            #     coroutine=SerpAPIWrapper(serpapi_api_key=os.environ["SERPAPI_API_KEY"]).arun,
            #     description="Useful when you need to answer questions about current events. You should ask targeted questions."
            # ),
            Tool(
                name="Aria",
                func=Agents.Aria.make_ask(level=level, memory=memory),
                coroutine=Agents.Aria.make_ask(level=level, memory=memory),
                description="Adria is a language model that can answer questions and generate text. Shes fast friendly and mildy creative always ready to help",
            ),
            Tool(
                name="Daisuke",
                func=Agents.Daisuke.make_ask(level=level, memory=memory),
                coroutine=Agents.Daisuke.make_ask(level=level, memory=memory),
                description="Daisuke is a language model that can answer questions and generate text. Shes fast friendly and extremely creative always and therefore sometimes lacks correctness and focus. As such she should have her work checked by a more precise agent.",
            ),
            Tool(
                name="Geoffrey",
                func=Agents.Geoffrey.make_ask(level=level, memory=memory),
                coroutine=Agents.Geoffrey.make_ask(level=level, memory=memory),
                description="Geoffrey is a language model that can answer questions and generate text. He is slow , thoughtful not creative and doesnt like to be asked too frequently.",
            ),
           Tool(
    name="search",
    func=search_bing,
    description="useful for when you need to answer questions about current events",
    coroutine=search_bing,
)
        ]



    def make_ask(self, memory, level: int):
        @retry(stop=stop_after_attempt(3))
        async def ask(
            input: str = "",
            agent=self,
        ) -> str:
            template = f"""Your name is {agent.name}. Please introduce yourself whenever speaking.
                            We are here to answer the question: "{input}". {{input}}
                            To do this effectively, you will follow a structured process:
                            Decompose the problem into parts. Use the functions to ask the most appropriate expert for each part.
                            You must only ask each expert a question. You must only respond with an answer.
                            You can only ask questions to functions. You cannot ask a question in response to a question.
                                0. You may not ask any question the same as or similar to that which has already been asked of an expert within memory.
                                1. All questions asked to an agent will have numeric level. e.g. "Level 2: What does crimson mean?"
                                2. The level will be decremented each time a question is asked.
                                3. This is a level {level} question.
                                4. For levels greater than 2 you MUST ask a decomposed question to an agent.
                                5. You will decrement the level by 1 each time when you receive a question, this new level should be passed to any functions you call.
                                7. Once the level reaches 0 then no more questions will be asked by you to any agent. You should then recombine the answers to the questions to form the answer to the original question.
                                8. When returning an answer to the original question you will assign a likelihood of your current assertion being correct.
                                8. You will brainstorm the answer step by step; reasoning carefully and taking all the facts into consideration..
                                9. The maximum number of functions the you can call is 3, after that you should then recombine the answers to the questions to form the answer to the original question.
                                10. You will check their answers based on science and the laws of physics , math and logic.
                                11. If at any time you realise that there is a flaw in the logic of an opinion you have  recieved you will backtrack to where the flaw occured.
                                12. If you realise any expert is wrong at any point then acknowledge this and backtrack to where they went wrong to start another train of thought.
                                13. Continue until all experts agree on the single most likely answer or the level reaches 0.
                                14. Summarise all the answers you have recieved and assign a likelihood of your current assertion being correct.
                                15. Any level other than 3 will be considered a partial answer and an internal thought, not a final answer and should not be displayed.
                            Remember, our goal is to answer the question: "{input}", repeat the question to yourself before each step to ensure you are on track.
                            the main question as effectively as possible. The history of the conversation is stored in the memory of the chatbot and is as follows: {{history}}"""

            if level > 0:
                llm = initialize_agent(
                    agent.tools(memory=memory, level=level - 1),
                    agent.model,
                    agent=AgentType.OPENAI_MULTI_FUNCTIONS,
                    verbose=True,
                    memory=memory,
                    prompt=template,
                )
                answer = await llm.arun(input=template)
            else:
                system_message_prompt = SystemMessagePromptTemplate.from_template(
                    template
                )

                chat = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=1)
                chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt])

                chain = ConversationChain(
                    llm=chat,
                    prompt=chat_prompt,
                    memory=memory,
                )
                # history and input are supplied by the conversationalbuffermemory
                answer = await chain.arun(
                    input=input,
                )

            print(f"Agent {self.name} says: {answer=}")
            return answer

        return ask

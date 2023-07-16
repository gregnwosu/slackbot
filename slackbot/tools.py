from slack_sdk.web.async_client import AsyncWebClient
from langchain.agents import initialize_agent, Tool
from langchain.agents import AgentType
from langchain.chat_models import ChatOpenAI
from slackbot.parsing.file.model import MimeType
import os
from enum import Enum
from typing import Any
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

import azure.cognitiveservices.speech as speechsdk
from typing import List

import os
from azure.cognitiveservices.speech import (
    SpeechSynthesizer,
    SpeechSynthesisOutputFormat,
    SpeechSynthesisResult,
)
from langchain.memory import ConversationBufferMemory
from dotenv import load_dotenv, find_dotenv
import io

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
        ConversationBufferMemory(),
        ChatOpenAI(
            model_name="gpt-3.5-turbo",
            temperature=1,
            openai_api_key=os.environ["OPENAI_API_KEY"],
        ),
    )
    Geoffrey = (
        "Geoffrey",
        os.environ["SLACK_BOT_TOKEN"],
        ConversationBufferMemory(),
        ChatOpenAI(
            model_name="gpt-4",
            temperature=0,
            openai_api_key=os.environ["OPENAI_API_KEY"],
        ),
    )

    def __init__(self, name: str, slack_key: str, memory: Any, model: Any) -> None:
        super().__init__()
        # self.name = name
        self.slack_key = slack_key
        self.memory = memory
        self.model = model
        self.slack_client: AsyncWebClient = AsyncWebClient(token=self.slack_key)

    def tools(self) -> list[Tool]:
        return [
            # Tool(
            #     name="Search",
            #     func=SerpAPIWrapper(serpapi_api_key=os.environ["SERPAPI_API_KEY"]).run,
            #     description="Useful when you need to answer questions about current events. You should ask targeted questions."
            # ),
            Tool(
                name="Adria",
                func=Agents.Aria.ask,
                description="Adria is a language model that can answer questions and generate text. Shes fast friendly and mildy creative always ready to help",
            ),
            Tool(
                name="Geoffrey",
                func=Agents.Geoffrey.ask,
                description="Geoffrey is a language model that can answer questions and generate text. He is slow , thoughtful not creative and doesnt like to be asked too frequently.",
            ),
        ]

    async def speak(self, text: str) -> str:
        subscription_key = "<your-subscription-key>"
        endpoint = "<your-endpoint>"
        speech_config = speechsdk.SpeechConfig(
            subscription="YOUR_SUBSCRIPTION_KEY", region="YOUR_REGION"
        )

        synthesizer: SpeechSynthesizer = SpeechSynthesizer(speech_config=speech_config)
        speech_config.set_speech_synthesis_output_format(
            SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3
        )

        result: SpeechSynthesisResult = await synthesizer.speak_text_async(text)
        result.audio_data
        data: bytes = result.audio_data

        response = await self.slack_client.files_upload_v2(
            channel="admin",
            file=data,
            filename="audio.mp3",
            filetype=MimeType.AUDIO_MP3.value,
            initial_comment=text,
        )
        return response["data"]

    async def ask(self, input: str) -> str:
        template = f"""

Your name is {self.name}. Please introduce yourself whenever speaking.

We are here to answer the question: "{input}".

To do this effectively, you will follow a structured process:

Decompose the problem into parts. Use the functions to ask the most appropriate expert for each part.
You must only ask each expert a question. You must only respond with an answer.
You can only ask questions to functions. You cannot ask a question in response to a question.

    1. All questions asked to an agent will be prefixed by a numeric level. e.g. "Level 2: What does crimson mean?"
    2. The level will be decremented each time a question is asked.
    3. If no level is specified then the level will be 3.
    4. You will decrement the level by 1 each time when you receive a question, this new level should be passed to any functions you call.
    5. Once the level reaches 0 then no more questions will be asked by you to any agent. You should then recombine the answers to the questions to form the answer to the original question.
    6. When returning an answer to the original question you will assign a likelihood of your current assertion being correct.
    7. You will brainstorm the answer step by step; reasoning carefully and taking all the facts into consideration..
    8. The maximum number of functions the you can call is 3, after that you should then recombine the answers to the questions to form the answer to the original question.
    9. You will check their answers based on science and the laws of physics , math and logic.
    10. If at any time you realise that there is a flaw in the logic of an opinion you have  recieved you will backtrack to where the flaw occured.
    11. If you realise any expert is wrong at any point then acknowledge this and backtrack to where they went wrong to start another train of thought.
    12. Continue until all experts agree on the single most likely answer or the level reaches 0.
    13. Any level other than 3 will be considered a partial answer and an internal thought, not a final answer and should not be displayed.

Remember, our goal is to answer the question: "{input}", repeat the question to yourself before each step to ensure you are on track.
 the main question as effectively as possible. The history of the conversation is stored in the memory of the chatbot and is as follows: {{history}}
"""
        system_message_prompt = SystemMessagePromptTemplate.from_template(template)

        human_template = "Heres the situation:\n\n{input}"
        human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

        chat_prompt = ChatPromptTemplate.from_messages(
            [system_message_prompt, human_message_prompt]
        )

        llm = initialize_agent(
            self.tools(),
            self.model,
            agent=AgentType.OPENAI_MULTI_FUNCTIONS,
            verbose=True,
            memory=self.memory,
        )
        # chain = ConversationChain(llm=llm, prompt=chat_prompt, memory=ConversationBufferMemory())
        answer = await llm.arun(input=template)
        # use self.slack_client to send message to slack
        # self.slack_client.chat_postMessage(channel="admin", text=answer)
        return answer

import pytest
from slackbot.functions import convo
from slackbot.tools import Agents, text_to_speech
from dotenv import load_dotenv, find_dotenv
from langchain.memory import ConversationSummaryBufferMemory
from langchain import OpenAI
import elevenlabs

load_dotenv(find_dotenv())


@pytest.mark.skip
async def test_convo():
    await convo(
        input="what is the capital of Bolivia", expert_name="Dave", channel="admin"
    )


# print(f"Result is {result=}")


@pytest.mark.asyncio
async def test_convo2():
    fn = Agents.Aria.make_ask(
        memory=ConversationSummaryBufferMemory(llm=OpenAI()), level=3
    )
    await fn(
        input="Why do modern day caucasians want to hide the fact they are descended from the ancient Edomites?"
    )


# test text to speech


@pytest.mark.asyncio
async def test_text_to_speech():
    text = "Hello, I am a robot. I am here to help you."

    data = await text_to_speech(text)
    assert data is not None
    # elevenlabs.play_audio(data)

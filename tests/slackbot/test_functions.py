import pytest
from slackbot.functions import convo
from slackbot.tools import Agents
from slackbot.tools import Conversation
from slackbot.speak import text_to_speech
from dotenv import load_dotenv, find_dotenv
from langchain.memory import ConversationSummaryBufferMemory
from langchain import OpenAI
import elevenlabs
import os
from slackbot.search import search_bing
load_dotenv(find_dotenv())


@pytest.mark.skip
async def test_convo():
    await convo(
        input="what is the capital of Bolivia", expert_name="Dave", channel="admin"
    )


# print(f"Result is {result=}")



@pytest.mark.asyncio
async def test_convo2():
    convo = Conversation(agent = None, level=3, memory=ConversationSummaryBufferMemory(llm=OpenAI(model="gpt-4")), channel="admin")
    result = await convo.ask(
        agent=Agents.Aria,
        input_question="religon can be seen as a social virus as, just like a conventional virus it has a method of replication (evangelism), infection (indoctrination) and incubation? Likewise chain letters are social virii. What other forms of social virii can you imagine?",
        level=2,
        channel = convo.channel,
        memory=convo.memory,
    )
    

# test text to speech

@pytest.mark.skip
@pytest.mark.asyncio
async def test_text_to_speech():
    text = "Hello, I am a robot. I am here to help you."

    data = await text_to_speech(text)
    assert data is not None
    # check if running from azure webapp
    if "GITHUB_ACTIONS" not in os.environ:
        elevenlabs.play(data)

@pytest.mark.skip
@pytest.mark.asyncio
async def test_search():
    query = "Mongolian Throat Singing"

    data = await search_bing(query)
    assert data is not None
    # check if running from azure webapp
    print(data)

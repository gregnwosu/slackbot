import pytest


#from slackbot.conversation import Conversation
#from slackbot.speak import text_to_speech
from dotenv import load_dotenv, find_dotenv
from slack_sdk.web.async_client import AsyncWebClient
# import elevenlabs
import os
from slackbot.search import search_bing
from slackbot.speak import speak


load_dotenv(find_dotenv())


@pytest.mark.skip
async def test_convo():
    # await convo(
    #     input="what is the capital of Bolivia", expert_name="Dave", channel="admin"
    # )
    pass


# print(f"Result is {result=}")


@pytest.mark.skip
@pytest.mark.asyncio
async def test_convo2():
    pass
    # convo = Conversation(agent = [], channel="C0595A85N4R")
    # result = await convo.ask(
       
    #     input_question="What is the likelihood of a nuclear war in the next 10 years?",
       
    #     channel = convo.channel,

    # )
    

# test text to speech

@pytest.mark.skip
@pytest.mark.asyncio
async def test_text_to_speech():
    text = "Hello, I am a robot. I am here to help you."

    # data = await text_to_speech(text)
    # assert data is not None
    # check if running from azure webapp
    

@pytest.mark.skip
@pytest.mark.asyncio
async def test_search():
    query = "Mongolian Throat Singing"

    data = await search_bing(query)
    assert data is not None
    # check if running from azure webapp
    print(data)


@pytest.mark.asyncio
async def test_speak():
    query = "Tell me that you love me"
    slack_client = AsyncWebClient(token=os.environ["SLACK_BOT_TOKEN"])
    await speak(input_question=query, agent=Agents.Aria, channel="C0595A85N4R", slack_client=slack_client)
    
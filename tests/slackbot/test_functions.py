

import pytest
from slackbot.functions import convo
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
@pytest.mark.asyncio
async def test_convo():
    result = await convo(input="what is the capital of Bolivia", expert_name="Dave", channel="admin")
    print(f"Result is {result=}")
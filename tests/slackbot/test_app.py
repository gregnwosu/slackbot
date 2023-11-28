import pytest
from dotenv import load_dotenv, find_dotenv

from slackbot import app


@pytest.mark.asyncio
async def test_flushes_cache():
    load_dotenv(find_dotenv())
    await app.root(None)





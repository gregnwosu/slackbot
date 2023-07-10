

import pytest
from slackbot.functions import convo

@pytest.mark.asyncio
async def test_convo():
    result = await convo(input="can you give me an answer", expert_name="Dave", channel="admin")
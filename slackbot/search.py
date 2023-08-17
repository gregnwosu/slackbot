import aiohttp

from slackbot.vault import get_secret
from slackbot.agent import Agents


mkt = "en-GB"


async def search_bing(
    input_question: str, agent: Agents = None, memory=None, channel=None, level=None
):
    primary_access_key = await get_secret("bing-service-access-key")
    endpoint = await get_secret("bing-service-endpoint")
    headers = {"Ocp-Apim-Subscription-Key": primary_access_key}
    params = {"q": input_question, "mkt": mkt}
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"{endpoint}v7.0/search", headers=headers, params=params
        ) as response:
            response.raise_for_status()
            return await response.json()

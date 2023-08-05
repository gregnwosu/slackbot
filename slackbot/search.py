import aiohttp

from slackbot.vault import get_secret

'''
This sample makes a call to the Bing Web Search API with a query and returns relevant web search.
Documentation: https://docs.microsoft.com/en-us/bing/search-apis/bing-web-search/overview
'''

# Add your Bing Search V7 subscription key and endpoint to your environment variables.

# # Query term(s) to search for. 
# query = "Microsoft"

# # Construct a request
# mkt = 'en-US'
# params = { 'q': query, 'mkt': mkt }
# headers = { 'Ocp-Apim-Subscription-Key': subscription_key }

async def search_bing(query):
    primary_access_key = await get_secret("bing-service-acccess-key")
    endpoint = await get_secret("bing-service-endpoint")
    headers = {"Ocp-Apim-Subscription-Key": primary_access_key}
    params = {"q": query, "count": 3}
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{endpoint}bing/v7.0/search", headers=headers, params=params) as response:
            response.raise_for_status()
            return await response.json()

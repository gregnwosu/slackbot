
from slackbot import app
import pytest
import json
from fastapi import status, Response
from starlette.testclient import TestClient
from unittest.mock import MagicMock, patch
import datetime
from httpx import AsyncClient
from slack_sdk.web.async_client import AsyncWebClient

from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.fastapi.async_handler import AsyncSlackRequestHandler

async def mock_say(utterance:str) -> None:
    return None

@pytest.fixture
def mock_slack_api_token_revoked_response():
    """Mocks a Slack API request to /api/users.profile.set and returns a "Token Revoked" payload
    Slack SDK uses urllib, so this is a bit hairy
    {'ok': False, 'error': 'token_revoked'}
    """
    with patch("slack_sdk.web.base_client.urlopen") as mock_urllib_open:
        mock_io_reader = MagicMock()
        mock_io_response = MagicMock()
        mock_io_reader.read.return_value = mock_io_response
        mock_io_response.decode.return_value = json.dumps({"ok": False, "error": "token_revoked"})
        mock_urllib_open.return_value = mock_io_reader
        yield mock_urllib_open

@pytest.fixture
def client():
    with TestClient(app.api) as client:
        yield client

@pytest.fixture
def async_slack_client():
    with AsyncWebClient( base_url="http://127.0.0.1:8000",token=app.SLACK_BOT_TOKEN) as client:
        yield client




@pytest.mark.asyncio
async def test_fastapi_routing():
    async with AsyncClient(app=app.api, base_url="http://127.0.0.1:8000") as ac:
        response = await ac.get("/")
    
    assert response.status_code == status.HTTP_200_OK

@pytest.mark.asyncio
async def test_app_mention():
    # This is a simplified version of the data Slack sends for an app_mention event
    timenow = datetime.datetime.now().timestamp()

    data2={'token': 'waNounRnAWVeA53FlYyaPaP8', 'team_id': 'T058PNE2HKP', 'api_app_id': 'A058SM2MXS6', 
          'event': {'client_msg_id': '399b2e89-719b-4172-ab1b-43e5d3d9d308',
                     'type': 'app_mention', 'text': '@Aria hi', 'user': 'U058V5QTW12', 
                     'ts': '1686966902.198599', 'blocks': [{'type': 'rich_text', 'block_id': 'EpPfS', 
                                                            'elements': [{'type': 'rich_text_section', 
                                                                          'elements': [{'type': 'user', 'user_id': 'U058V6AG10C'}, 
                                                                                       {'type': 'text', 'text': ' hi'}]}]}], 'team': 'T058PNE2HKP', 'channel': 'C0595A85N4R', 'event_ts': '1686966902.198599'}, 'type': 'event_callback', 'event_id': 'Ev05D00M7VS7', 'event_time': 1686966902, 
                                                                                       'authorizations': [{'enterprise_id': None, 'team_id': 'T058PNE2HKP', 'user_id': 'U058V6AG10C', 'is_bot': True, 'is_enterprise_install': False}], 'is_ext_shared_channel': False, 
                                                                             'event_context': '4-eyJldCI6ImFwcF9tZW50aW9uIiwidGlkIjoiVDA1OFBORTJIS1AiLCJhaWQiOiJBMDU4U00yTVhTNiIsImNpZCI6IkMwNTk1QTg1TjRSIn0'}
    app.app.request_verification_enabled=False
    
    
    result = await app.handle_mentions(data2, say=mock_say)
        
    assert result.status_code == status.HTTP_200_OK 
    print(f"{dir(result)=}")
    assert result.body == b"OKieDokie"
    
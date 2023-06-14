
from slackbot import app
import pytest
import json

from starlette.testclient import TestClient

# @pytest.fixture
# def client():
#     async_client = app.cached_slack_client()
#     yield async_client

async def async_print(*args):
    print(*args)

#@pytest.mark.skip(reason="not implemented")
@pytest.mark.asyncio
async def test_app_mention():
    # This is a simplified version of the data Slack sends for an app_mention event
    data = {
        "token": "Jhj5dZrVaK7ZwHHjRyZWjbDl",
        "team_id": "T0MJR11A4",
        "api_app_id": "A0KRD7HC3",
        "event": {
            "type": "app_mention",
            "user": "U0MJRG1AL",
            "text": "<@U0MJRG1AL> Hello",
            "ts": "1516229207.000133",
            "channel": "D0MDKDYKC",
            "event_ts": "1516229207000133"
        },
        "type": "event_callback",
        "event_id": "Ev0MDKHSKG",
        "event_time": 1516229207,
        "authed_users": ["U0MJRG1AL"]
    }


#     data = {'token': 'waNounRnAWVeA53FlYyaPaP8', 'team_id': 'T058PNE2HKP', 'context_team_id': 'T058PNE2HKP', 'context_enterprise_id': None, 'api_app_id': 'A058SM2MXS6', 
#  'event': {'type': 'file_change', 'file_id': 'F05BEHD7BRT', 'user_id': 'U058V5QTW12', 'file': {'id': 'F05BEHD7BRT'}, 'event_ts': '1686181314.046100'}, 'type': 'event_callback', 'event_id': 'Ev05BHBXRXNF', 'event_time': 1686181314, 'authorizations': [{'enterprise_id': None, 'team_id': 'T058PNE2HKP', 'user_id': 'U058V6AG10C', 'is_bot': True, 'is_enterprise_install': False}], 'is_ext_shared_channel': False, 'event_context': '4-eyJldCI6ImZpbGVfY2hhbmdlIiwidGlkIjoiVDA1OFBORTJIS1AiLCJhaWQiOiJBMDU4U00yTVhTNiIsImZpZCI6IkYwNUJFSEQ3QlJUIn0'}

    response = await app.handle_mentions(body =data, say=async_print)

    #response = client.post("/slack/events", data=json.dumps(data), headers={"Content-Type": "application/json"})
    print(response)
    #assert response.status_code == 200
    #assert "Sure, I'll get right on that!" in response.text
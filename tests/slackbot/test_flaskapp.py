
from slackbot import app
import pytest
import json

from starlette.testclient import TestClient


@pytest.fixture
def client():
    with TestClient(app.fastapi_app) as client:
        yield client


def test_example(client):
    response = client.get("/example")
    assert response.status_code == 404

def test_app_mention(client):
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

    response = client.post("/slack/events", data=json.dumps(data), headers={"Content-Type": "application/json"})

    assert response.status_code == 200
    assert "Sure, I'll get right on that!" in response.text
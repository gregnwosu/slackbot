
from slackbot import app
import pytest


from starlette.testclient import TestClient


@pytest.fixture
def client():
    with TestClient(app.fastapi_app) as client:
        yield client



def test_example(client):
    response = client.get("/example")
    assert response.status_code == 404

from slackbot import app
import pytest


@pytest.fixture
def client():
    app.slack_app.config['TESTING'] = True

    with app.slack_app.test_client() as client:
        yield client



def test_hello_world(client):
    response = client.get('/hello')
    # assert response.data == b'Hello, World!'
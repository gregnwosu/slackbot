
from slackbot import app
import pytest


@pytest.fixture
def client():
    app.fastapi_app.config['TESTING'] = True

    with app.fastapi_app.test_client() as client:
        yield client



def test_hello_world(client):
    response = client.get('/hello')
    # assert response.data == b'Hello, World!'
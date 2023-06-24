
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

from slackbot.parsing.message.event import MessageSubType

async def mock_say(utterance:str, channel=None) -> None:
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
@pytest.mark.parametrize("data,model_class", [
    ({'event':{
	"type": "message",
	"channel": "#admin",
	"text": "hi can i join the channel?",
	"ts": "1403051575.000407",
	"user": "U123ABC456"
}}, MessageSubType.message),({'token': 'waNounRnAWVeA53FlYyaPaP8', 'team_id': 'T058PNE2HKP', 'context_team_id': 'T058PNE2HKP', 'context_enterprise_id': None, 'api_app_id': 'A058SM2MXS6', 
                            'event': {'type': 'message', 'text': '', 
                                    
                                        'files': [{'id': 'F05E1RVFAHG', 'created': 1687569259, 'timestamp': 1687569259, 'name': 'audio_message.webm', 'title': 'audio_message.webm', 'mimetype': 'audio/webm', 'filetype': 'webm', 'pretty_type': 'WebM', 'user': 'U058V5QTW12', 'user_team': 'T058PNE2HKP', 'editable': False, 'size': 112070, 'mode': 'hosted', 'is_external': False, 'external_type': '', 'is_public': True, 'public_url_shared': False, 'display_as_bot': False, 'username': '', 'subtype': 'slack_audio', 'transcription': {'status': 'processing'}, 'url_private': 'https://files.slack.com/files-tmb/T058PNE2HKP-F05E1RVFAHG-0f5c6bb30c/audio_message_audio.mp4', 'url_private_download': 'https://files.slack.com/files-tmb/T058PNE2HKP-F05E1RVFAHG-0f5c6bb30c/download/audio_message_audio.mp4', 'duration_ms': 6899, 'aac': 'https://files.slack.com/files-tmb/T058PNE2HKP-F05E1RVFAHG-0f5c6bb30c/audio_message_audio.mp4', 'audio_wave_samples': [1, 1, 59, 100, 76, 86, 83, 77, 47, 1, 25, 67, 70, 43, 65, 68, 49, 2, 1, 1, 1, 8, 30, 23, 29, 3, 1, 2, 2, 35, 54, 46, 30, 28, 43, 43, 37, 34, 35, 25, 1, 0, 0, 0, 0, 0, 1, 0, 0, 9, 59, 58, 52, 54, 49, 45, 36, 3, 4, 40, 35, 20, 2, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 27, 25, 17, 3, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 3, 0], 'media_display_type': 'audio', 'permalink': 'https://ai-experimentshq.slack.com/files/U058V5QTW12/F05E1RVFAHG/audio_message.webm', 'permalink_public': 'https://slack-files.com/T058PNE2HKP-F05E1RVFAHG-2dfcb62184', 'has_rich_preview': False, 'file_access': 'visible'}], 
                                        'upload': False, 'user': 'U058V5QTW12', 'display_as_bot': False, 'ts': '1687569263.664299', 'client_msg_id': '65e324ef-ae08-4098-99af-68f54b01c0cd', 'channel': 'C0595A85N4R', 'subtype': 'file_share', 'event_ts': '1687569263.664299', 'channel_type': 'channel'}, 
                                        
                                        
                                        'type': 'event_callback', 'event_id': 'Ev05DV6JSKEJ', 'event_time': 1687569263, 'authorizations': [{'enterprise_id': None, 'team_id': 'T058PNE2HKP', 'user_id': 'U058V6AG10C', 'is_bot': True, 'is_enterprise_install': False}], 'is_ext_shared_channel': False, 'event_context': '4-eyJldCI6Im1lc3NhZ2UiLCJ0aWQiOiJUMDU4UE5FMkhLUCIsImFpZCI6IkEwNThTTTJNWFM2IiwiY2lkIjoiQzA1OTVBODVONFIifQ'} , MessageSubType.file_share)

])
async def test_message(data, model_class):
    # This is a simplified version of the data Slack sends for an app_mention event
    model = await app.handle_message(data, say=mock_say) 
    assert isinstance(model, model_class.value)

@pytest.mark.asyncio
@pytest.mark.parametrize("data", [({'token': 'waNounRnAWVeA53FlYyaPaP8', 'team_id': 'T058PNE2HKP', 'api_app_id': 'A058SM2MXS6', 
          'event': {'client_msg_id': '399b2e89-719b-4172-ab1b-43e5d3d9d308',
                     'type': 'app_mention', 'text': '@Aria hi', 'user': 'U058V5QTW12', 
                     'ts': '1686966902.198599', 'blocks': [{'type': 'rich_text', 'block_id': 'EpPfS', 
                                                            'elements': [{'type': 'rich_text_section', 
                                                                          'elements': [{'type': 'user', 'user_id': 'U058V6AG10C'}, 
                                                                                       {'type': 'text', 'text': ' hi'}]}]}], 'team': 'T058PNE2HKP', 'channel': 'C0595A85N4R', 'event_ts': '1686966902.198599'}, 'type': 'event_callback', 'event_id': 'Ev05D00M7VS7', 'event_time': 1686966902, 
                                                                                       'authorizations': [{'enterprise_id': None, 'team_id': 'T058PNE2HKP', 'user_id': 'U058V6AG10C', 'is_bot': True, 'is_enterprise_install': False}], 'is_ext_shared_channel': False, 
                                                                             'event_context': '4-eyJldCI6ImFwcF9tZW50aW9uIiwidGlkIjoiVDA1OFBORTJIS1AiLCJhaWQiOiJBMDU4U00yTVhTNiIsImNpZCI6IkMwNTk1QTg1TjRSIn0'}),
                                                                             
                                                                             ({'token': 'waNounRnAWVeA53FlYyaPaP8', 'team_id': 'T058PNE2HKP', 'api_app_id': 'A058SM2MXS6', 'event': {'type': 'app_mention', 'text': '@Ariat', 'files': [{'id': 'F05DV3QQZ9U', 'created': 1687565352, 'timestamp': 1687565352, 'name': 'audio_message.webm', 'title': 'audio_message.webm', 'mimetype': 'audio/webm', 'filetype': 'webm', 'pretty_type': 'WebM', 'user': 'U058V5QTW12', 'user_team': 'T058PNE2HKP', 'editable': False, 'size': 67372, 'mode': 'hosted', 'is_external': False, 'external_type': '', 'is_public': True, 'public_url_shared': False, 'display_as_bot': False, 'username': '', 'subtype': 'slack_audio', 'transcription': {'status': 'processing'}, 'url_private': 'https://files.slack.com/files-tmb/T058PNE2HKP-F05DV3QQZ9U-5281c58260/audio_message_audio.mp4', 'url_private_download': 'https://files.slack.com/files-tmb/T058PNE2HKP-F05DV3QQZ9U-5281c58260/download/audio_message_audio.mp4', 'duration_ms': 4144, 'aac': 'https://files.slack.com/files-tmb/T058PNE2HKP-F05DV3QQZ9U-5281c58260/audio_message_audio.mp4', 'audio_wave_samples': [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 7, 86, 78, 29, 37, 94, 64, 23, 5, 22, 60, 61, 66, 49, 36, 100, 96, 39, 48, 23, 3, 7, 32, 32, 42, 30, 7, 30, 21, 16, 35, 48, 50, 25, 36, 31, 23, 8, 1, 1, 11, 41, 24, 14, 5, 2, 1, 0, 1, 1, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 1, 0, 1, 0, 0, 0], 'media_display_type': 'audio', 'permalink': 'https://ai-experimentshq.slack.com/files/U058V5QTW12/F05DV3QQZ9U/audio_message.webm', 'permalink_public': 'https://slack-files.com/T058PNE2HKP-F05DV3QQZ9U-422d714b58', 'is_starred': False, 'has_rich_preview': False, 'file_access': 'visible'}], 'upload': False, 'user': 'U058V5QTW12', 'display_as_bot': False, 'ts': '1687565355.549719', 'blocks': [{'type': 'rich_text', 'block_id': 'tQSot', 'elements': [{'type': 'rich_text_section', 'elements': [{'type': 'user', 'user_id': 'U058V6AG10C'}, {'type': 'text', 'text': ' t'}]}]}], 'client_msg_id': '279ff017-c252-45f0-985f-c89c7496f2e4', 'channel': 'C0595A85N4R', 'event_ts': '1687565355.549719'}, 'type': 'event_callback', 'event_id': 'Ev05DM79KW4F', 'event_time': 1687565355, 'authorizations': [{'enterprise_id': None, 'team_id': 'T058PNE2HKP', 'user_id': 'U058V6AG10C', 'is_bot': True, 'is_enterprise_install': False}], 'is_ext_shared_channel': False, 'event_context': '4-eyJldCI6ImFwcF9tZW50aW9uIiwidGlkIjoiVDA1OFBORTJIS1AiLCJhaWQiOiJBMDU4U00yTVhTNiIsImNpZCI6IkMwNTk1QTg1TjRSIn0'} )])
async def test_app_mention(data):
    # This is a simplified version of the data Slack sends for an app_mention event
    result = await app.handle_mentions(data, say=mock_say)
    assert result.status_code == status.HTTP_200_OK 
    print(f"{dir(result)=}")
    assert result.body == b"OKieDokie"


    
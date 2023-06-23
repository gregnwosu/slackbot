import pytest 
import datetime
import os

from slack_sdk import WebClient
from slackbot.parsing.appmention.event import AppMentionEvent
from slackbot.parsing.base.model import BlockData, BlockElement, BlockElementData, BlockElementDataType, BlockElementType, BlockType, EventType
from slackbot.parsing.file.model import FileAccess, FileMode, FileShare, FileShares, FileSubType, FileType, Locale, MimeType, Preview, Transcription, TranscriptionStatus
from slackbot.parsing.file.event import FileInfo, FileEvent, FileDetails
import dotenv
from starlette.testclient import TestClient
from slackbot import app 
from fastapi import status

@pytest.fixture()
def web_client():
    dotenv.load_dotenv(dotenv.find_dotenv())
    return WebClient(token=os.environ["SLACK_BOT_TOKEN"])
    


@pytest.mark.parametrize("event_in, expected", [
    ({'client_msg_id': '07fc5446-f407-4a08-a215-f75be8cfa0f9', 'type': 'app_mention', 'text': 'hey',
  'user': 'U058V5QTW12', 'ts': '1685890319.156619', 
  'blocks': [
      {'type': 'rich_text', 'block_id': 'qui', 
       'elements': [
           {'type': 'rich_text_section', 
            'elements': [
                {'type': 'user', 'user_id': 'U058V6AG10C'}, 
                {'type': 'text', 'text': ' hey'}]
            }
        ]
     }
  ], 'team': 'T058PNE2HKP', 
            'channel': 'C0595A85N4R', 
            'event_ts': '1685890319.156619'
}, AppMentionEvent(client_msg_id='07fc5446-f407-4a08-a215-f75be8cfa0f9', type=EventType.APP_MENTION, text='hey', user='U058V5QTW12',
                   ts='1685890319.156619', blocks=[BlockData(type=BlockType.RICH_TEXT, block_id='qui', elements=[BlockElement(type=BlockElementType.RICH_TEXT_SECTION, elements=[BlockElementData(type=BlockElementDataType.USER, user_id='U058V6AG10C', text=None), BlockElementData(type=BlockElementDataType.TEXT, user_id=None, text=' hey')])])], team='T058PNE2HKP', channel='C0595A85N4R', event_ts='1685890319.156619')),
   
])
def test_app_mention_event(event_in, expected):
    actual = AppMentionEvent(**event_in)
    assert actual == expected, repr(actual)
    

@pytest.mark.parametrize("event_in, expected, expected_file_info",  [
    ({'type': 'file_shared', 'file_id': 'F05BL5K8RLG', 'user_id': 'U058V5QTW12', 
      'file': {'id': 'F05BL5K8RLG'}, 'channel_id': 'C0595A85N4R', 'event_ts': '1685914835.005200'}, 
      FileEvent(type=EventType.FILE_SHARED, file_id='F05BL5K8RLG', user_id="U058V5QTW12", file=FileDetails(id="F05BL5K8RLG"), channel_id="C0595A85N4R", event_ts="1685914835.005200"),
      FileInfo(id='F05BL5K8RLG', created=1685914831, timestamp=datetime.datetime(2023, 6, 4, 21, 40, 31, tzinfo=datetime.timezone.utc), name='audio_message.webm', title='audio_message.webm', mimetype=MimeType.AUDIO_WEBM, filetype=FileType.WEBM, pretty_type='WebM', user='U058V5QTW12', user_team='T058PNE2HKP', editable=False, size=137519, mode=FileMode.HOSTED, is_external=False, external_type='', is_public=True, public_url_shared=False, display_as_bot=False, username='', subtype=FileSubType.SLACK_AUDIO, transcription=Transcription(status=TranscriptionStatus.COMPLETE, locale=Locale.EN_US, preview=Preview(content='Back to just, you know, the work flow here really quick. This is a great starting point. And then after this way you can do, you can have another.', has_more=False)),
                duration_ms=8458, 
                url_private='https://files.slack.com/files-tmb/T058PNE2HKP-F05BL5K8RLG-c298d7bc9c/audio_message_audio.mp4',
                url_private_download='https://files.slack.com/files-tmb/T058PNE2HKP-F05BL5K8RLG-c298d7bc9c/download/audio_message_audio.mp4',
                vtt='https://files.slack.com/files-tmb/T058PNE2HKP-F05BL5K8RLG-c298d7bc9c/file.vtt?_xcb=a3a01',
                aac='https://files.slack.com/files-tmb/T058PNE2HKP-F05BL5K8RLG-c298d7bc9c/audio_message_audio.mp4', 
                audio_wave_samples=[12, 8, 8, 3, 4, 5, 15, 32, 4, 11, 24, 27, 21, 4, 3, 3, 3, 3, 6, 27, 15, 11, 3, 3, 3, 10, 38, 29, 31, 4, 6, 59, 30, 4, 8, 54, 49, 3, 14, 35, 39, 36, 32, 7, 93, 36, 5, 14, 13, 4, 4, 3, 4, 4, 4, 4, 14, 7, 93, 100, 16, 38, 55, 14, 75, 44, 4, 6, 31, 48, 29, 12, 4, 8, 23, 13, 7, 18, 14, 12, 10, 13, 7, 12, 30, 2, 18, 14, 5, 10, 17, 15, 9, 38, 47, 49, 23, 44, 41, 57], media_display_type=MimeType.AUDIO, 
                permalink='https://ai-experimentshq.slack.com/files/U058V5QTW12/F05BL5K8RLG/audio_message.webm', 
                permalink_public='https://slack-files.com/T058PNE2HKP-F05BL5K8RLG-80cd5cc6fa',
                is_starred=False, shares=FileShares(public={'C0595A85N4R': [FileShare(reply_users=[], reply_users_count=0, reply_count=0, ts=datetime.datetime(2023, 6, 4, 21, 40, 36, 857269, tzinfo=datetime.timezone.utc), channel_name='admin', team_id='T058PNE2HKP', share_user_id='U058V6AG10C'), FileShare(reply_users=[], reply_users_count=0, reply_count=0, ts=datetime.datetime(2023, 6, 4, 21, 40, 35, 606609, tzinfo=datetime.timezone.utc), channel_name='admin', team_id='T058PNE2HKP', share_user_id='U058V5QTW12')]}), channels=['C0595A85N4R'], groups=[], ims=[], has_more_shares=False, has_rich_preview=False, file_access=FileAccess.VISIBLE, comments_count=0) )])
def test_file_shared_event(event_in: dict, expected: FileEvent, expected_file_info: FileInfo, web_client: WebClient):
    actual: FileEvent = FileEvent(**event_in)
    assert actual == expected, repr(actual)
    
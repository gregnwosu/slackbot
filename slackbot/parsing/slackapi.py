
from dataclasses import dataclass
import pydantic
from enum import Enum 
import datetime as dt
from typing import List, Optional, Dict
from urllib.parse import urlparse
from urllib.parse import ParseResult    
from logging import Logger
logger = Logger(__name__)
from slack_sdk import WebClient

#AppMentionData

class EventType(Enum):
    APP_MENTION = "app_mention"
    FILE_SHARED = "file_shared"
    FILE_CHANGE = "file_change"

class BlockType(Enum):
    RICH_TEXT = "rich_text"

class BlockElementType(Enum):
    RICH_TEXT_SECTION = "rich_text_section"

class BlockElementDataType(Enum):
    USER = "user"
    TEXT = "text"

class BlockElementData(pydantic.BaseModel):
    type: BlockElementDataType
    user_id: Optional[str] = None
    text: Optional[str] = None
    @pydantic.validator('type')
    def convert_to_blockelementdata_type(cls, value):
        return BlockElementDataType(value)

class BlockElement(pydantic.BaseModel):
    type: BlockElementType
    elements: List[BlockElementData]
    @pydantic.validator('type')
    def convert_to_blockelement_type(cls, value):
        return BlockElementType(value)

class BlockData(pydantic.BaseModel):
    type : BlockType
    block_id: str
    elements : List[BlockElement]
    
    
    @pydantic.validator('type')
    @classmethod
    def convert_to_block_type(cls, value):
        return BlockType(value)


class AppMentionEvent(pydantic.BaseModel):
    client_msg_id: str
    type: EventType
    text:  str 
    user: str
    ts:  dt.datetime
    blocks: List[BlockData]
    team: str 
    channel: str
    event_ts: dt.datetime
    
    @pydantic.validator('type')
    @classmethod
    def convert_to_event_type(cls, value):
        return EventType(value)
    



class FileDetails(pydantic.BaseModel):
    id: str
class FileEvent(pydantic.BaseModel):
    type: EventType
    file_id: str
    user_id: str
    file: FileDetails
    channel_id: str
    event_ts: dt.datetime
    
    @pydantic.validator('type')
    @classmethod
    def convert_to_event_type(cls, value):
        return EventType(value)
    
    def file_info(self, web_client: WebClient):
        response = web_client.files_info(file=self.file_id)
        assert response["ok"], f"Slack API call failed with error: {response['error']}"
        return FileInfo(**response["file"])


{'token': 'waNounRnAWVeA53FlYyaPaP8', 'team_id': 'T058PNE2HKP', 'context_team_id': 'T058PNE2HKP', 'context_enterprise_id': None, 'api_app_id': 'A058SM2MXS6', 
 'event': {'type': 'file_change', 'file_id': 'F05BEHD7BRT', 'user_id': 'U058V5QTW12', 'file': {'id': 'F05BEHD7BRT'}, 'event_ts': '1686181314.046100'}, 'type': 'event_callback', 'event_id': 'Ev05BHBXRXNF', 'event_time': 1686181314, 'authorizations': [{'enterprise_id': None, 'team_id': 'T058PNE2HKP', 'user_id': 'U058V6AG10C', 'is_bot': True, 'is_enterprise_install': False}], 'is_ext_shared_channel': False, 'event_context': '4-eyJldCI6ImZpbGVfY2hhbmdlIiwidGlkIjoiVDA1OFBORTJIS1AiLCJhaWQiOiJBMDU4U00yTVhTNiIsImZpZCI6IkYwNUJFSEQ3QlJUIn0'}

#File Shared Event

{'id': 'F05BL5K8RLG', 'created': 1685914831, 'timestamp': 1685914831, 'name': 'audio_message.webm', 
    'title': 'audio_message.webm', 'mimetype': 'audio/webm', 'filetype': 'webm', 'pretty_type': 'WebM',
    'user': 'U058V5QTW12', 'user_team': 'T058PNE2HKP', 'editable': False, 'size': 137519, 'mode': 'hosted',
        'is_external': False, 'external_type': '', 'is_public': True, 'public_url_shared': False, 'display_as_bot': False, 
        'username': '', 'subtype': 'slack_audio', 
        'transcription': {'status': 'complete', 'locale': 'en-US', 
                        'preview': {'content': 'Back to just, you know, the work flow here really quick. This is a great starting point. And then after this way you can do, you can have another.',
                                    'has_more': False}
                        },
    'url_private': 'https://files.slack.com/files-tmb/T058PNE2HKP-F05BL5K8RLG-c298d7bc9c/audio_message_audio.mp4', 
    'url_private_download': 'https://files.slack.com/files-tmb/T058PNE2HKP-F05BL5K8RLG-c298d7bc9c/download/audio_message_audio.mp4', 
    'vtt': 'https://files.slack.com/files-tmb/T058PNE2HKP-F05BL5K8RLG-c298d7bc9c/file.vtt?_xcb=a3a01', 
    'duration_ms': 8458, 
    'aac': 'https://files.slack.com/files-tmb/T058PNE2HKP-F05BL5K8RLG-c298d7bc9c/audio_message_audio.mp4',
    'audio_wave_samples': [12, 8, 8, 3, 4, 5, 15, 32, 4, 11, 24, 27, 21, 4, 3, 3, 3, 3, 6, 27, 15, 11, 3, 3, 3, 10, 38, 29, 31, 4, 6, 59, 30, 4, 8, 54, 49, 3, 14, 35, 39, 36, 32, 7, 93, 36, 5, 14, 13, 4, 4, 3, 4, 4, 4, 4, 14, 7, 93, 100, 16, 38, 55, 14, 75, 44, 4, 6, 31, 48, 29, 12, 4, 8, 23, 13, 7, 18, 14, 12, 10, 13, 7, 12, 30, 2, 18, 14, 5, 10, 17, 15, 9, 38, 47, 49, 23, 44, 41, 57], 
    'media_display_type': 'audio', 
    'permalink': 'https://ai-experimentshq.slack.com/files/U058V5QTW12/F05BL5K8RLG/audio_message.webm',
    'permalink_public': 'https://slack-files.com/T058PNE2HKP-F05BL5K8RLG-80cd5cc6fa', 
    'is_starred': False,
    'shares': {'public': {'C0595A85N4R': [
                                {'reply_users': [], 'reply_users_count': 0, 'reply_count': 0, 'ts': '1685914836.857269', 
                                'channel_name': 'admin', 'team_id': 'T058PNE2HKP', 'share_user_id': 'U058V6AG10C'}, 
                                {'reply_users': [], 'reply_users_count': 0, 'reply_count': 0, 'ts': '1685914835.606609', 
                                'channel_name': 'admin', 'team_id': 'T058PNE2HKP', 'share_user_id': 'U058V5QTW12'}
                                ]
                        }
            },
                                                                                                                
                                                                                                                
    'channels': ['C0595A85N4R'], 
    'groups': [], 
    'ims': [], 
    'has_more_shares': False, 
    'has_rich_preview': False, 
    'file_access': 'visible', 
    'comments_count': 0}

class MimeType(str, Enum):
    AUDIO_WEBM = "audio/webm"
    AUDIO = "audio"

class FileType(str, Enum):
    WEBM = "webm"

class FileMode(str, Enum):
    HOSTED = "hosted"

class FileSubType(str, Enum):
    SLACK_AUDIO = "slack_audio"

class Locale(Enum):
    EN_US = 'en-US'
    FR_FR = 'fr-FR'
    DE_DE = 'de-DE'
    ES_ES = 'es-ES'
    EN_GB = 'en-GB'

class Preview(pydantic.BaseModel):
    content: str
    has_more: bool

class TranscriptionStatus(str, Enum):
    COMPLETE = "complete"
    processing = "processing"
class Transcription(pydantic.BaseModel):
    status: TranscriptionStatus
    locale: Locale
    preview: Preview

class FileAccess(str, Enum):
    VISIBLE = "visible"

class FileShare(pydantic.BaseModel):
    reply_users: List[str]
    reply_users_count: int
    reply_count: int
    ts: dt.datetime
    channel_name: str
    team_id: str
    share_user_id: str

class FileShares(pydantic.BaseModel):
    public: Dict[str, List[FileShare]]






   


class FileInfo(pydantic.BaseModel):
    id: str
    created: int
    timestamp: dt.datetime
    name: str
    title: str
    mimetype: MimeType 
    filetype: FileType
    pretty_type: str
    user: str
    user_team: str
    editable: bool
    size: int
    mode: FileMode
    is_external: bool
    external_type: str
    is_public: bool
    public_url_shared: bool
    display_as_bot: bool
    username: str
    subtype: FileSubType
    transcription: Transcription
    url_private: str
    url_private_download: str
    vtt: str
    duration_ms: int
    aac: str
    audio_wave_samples: List[int]
    media_display_type: MimeType
    permalink: str
    permalink_public: str
    is_starred: bool
    shares: FileShares
    channels: List[str]
    groups: List[str]
    ims: List[str]
    has_more_shares: bool
    has_rich_preview: bool
    file_access: FileAccess 
    comments_count: int

    
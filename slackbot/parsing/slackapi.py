
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
import requests 

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
    #channel_id: str
    event_ts: dt.datetime
    
    @pydantic.validator('type')
    @classmethod
    def convert_to_event_type(cls, value):
        return EventType(value)
    
    def file_info(self, web_client: WebClient):
        response = web_client.files_info(file=self.file_id)
        assert response["ok"], f"Slack API call failed with error: {response['error']}"
        return FileInfo(**response["file"])


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

    @property
    def full_transcript(self) -> Optional[str]:
        # return the value pointed to by the vtt url
        if self.vtt:
            response: requests.Response = requests.get(self.vtt)
            response.raise_for_status()
            return response.text()
        return None

    
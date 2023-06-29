import re
import aiohttp
from slack_sdk.web.async_client import AsyncWebClient
from dataclasses import dataclass
import pydantic
from enum import Enum 
import datetime as dt
from typing import List, Optional, Dict
from urllib.parse import urlparse
from urllib.parse import ParseResult    
from logging import Logger
from slack_sdk import WebClient
from slackbot.parsing.base.model import EventType, BlockType, BlockElementType, BlockElementDataType, BlockElementData, BlockElement, BlockData
from slackbot.parsing.file.model import MimeType, FileType, FileMode, FileSubType, Locale, Preview, TranscriptionStatus, Transcription, FileAccess, FileShare, FileShares
from aiohttp import BasicAuth, web
logger = Logger(__name__)

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
    
    async def file_info(self, web_client: AsyncWebClient) -> "FileInfo":
        response = await web_client.files_info(file=self.file_id)
        assert response["ok"], f"Slack API call failed with error: {response['error']}"
        return FileInfo(**response["file"])


    


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
    vtt: Optional[str]
    duration_ms: int
    aac: str
    audio_wave_samples: List[int]
    media_display_type: MimeType
    permalink: str
    permalink_public: str
    is_starred: Optional[bool]
    shares: Optional[FileShares]
    channels: Optional[List[str]]
    groups: Optional[List[str]]
    ims: Optional[List[str]]
    has_more_shares: Optional[bool]
    has_rich_preview: bool
    file_access: FileAccess 
    comments_count: Optional[int] 

    @staticmethod
    def strip_vtt(text:str) -> str:
        # Remove WEBVTT line
        text = re.sub(r'^WEBVTT\s+', '', text, flags=re.MULTILINE)
        # Remove timestamped lines
        text = re.sub(r'\d{2}:\d{2}:\d{2}\.\d{3}\s+-->\s+\d{2}:\d{2}:\d{2}\.\d{3}\s+', '', text)
        # Remove preceding dashes
        text = re.sub(r'^-\s+', '', text, flags=re.MULTILINE)
        return text

    async def vtt_txt(self, bearer_auth) -> str:
        if not self.vtt:
            return ""
        async with aiohttp.ClientSession() as session:
            async with session.get(self.vtt, auth=bearer_auth) as response:
                 response.raise_for_status()
                 return self.strip_vtt(await response.text())
                 
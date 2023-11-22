import re
import aiohttp
from slack_sdk.web.async_client import AsyncWebClient
import pydantic
import datetime as dt
from typing import List, Optional
from logging import Logger
from slackbot.parsing.base.model import EventType
from slackbot.parsing.file.model import MimeType, FileType, FileMode, FileSubType, Transcription, FileAccess, FileShares
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

    @pydantic.field_validator('type')
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
    aac: Optional[str] = None
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
    def strip_vtt(vtt_string):
        # Split the string into lines
        lines = vtt_string.split('\n')
        pattern = r'^[a-zA-Z.!\-\(\)]'
        # Remove timestamp lines
        prose_lines = [line for line in lines if  re.match(pattern, line)]
        
        # Remove leading and trailing newlines
        stripped_prose = ' '.join(prose_lines).strip().replace('-', '').replace('WEBVTT', '')
        
        return stripped_prose

    async def vtt_txt(self, token:str) -> str:
        if not self.vtt:
            return ""
        headers = {'authorization': f'Bearer {token}'}
        async with aiohttp.ClientSession() as session:
            async with session.get(self.vtt, headers=headers) as response:
                 response.raise_for_status()
                 return self.strip_vtt(await response.text())
                 
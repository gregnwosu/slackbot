import pydantic
from typing import List, Optional, Set
import datetime as dt
from enum import Enum

from slackbot.parsing.base.model import ChannelType
from slackbot.parsing.file.event import FileInfo

class MessageEvent(pydantic.BaseModel):
    type: str
    channel: str
    user: str
    text: str
    ts: dt.datetime
    event_ts: Optional[dt.datetime]
    channel_type: Optional[ChannelType]

class BotMessageEvent(pydantic.BaseModel):
    type: str
    subtype: str
    ts: dt.datetime
    text: str
    bot_id: str
    username: str
    icons: Set[str]

class FileShareMessageEvent(pydantic.BaseModel):
    type: str
    text: str
    files: List[FileInfo]
    upload: bool
    user: str
    display_as_bot: bool
    ts: dt.datetime
    client_msg_id: str
    channel: str
    subtype: str
    event_ts: dt.datetime
    channel_type: Optional[ChannelType]


class MessageSubType(Enum):
    bot_message = BotMessageEvent
    message = MessageEvent
    file_share = FileShareMessageEvent
    

    @classmethod
    def __missing__(cls, value):
        # Define the behavior for the default member
        return cls.message
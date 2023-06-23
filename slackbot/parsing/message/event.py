import pydantic
from typing import Set
import datetime as dt
from enum import Enum

class MessageEvent(pydantic.BaseModel):
    type: str
    channel: str
    user: str
    text: str
    ts: dt.datetime

class BotMessageEvent(pydantic.BaseModel):
    type: str
    subtype: str
    ts: dt.datetime
    text: str
    bot_id: str
    username: str
    icons: Set[str]

class MessageSubType(Enum):
    bot_message = BotMessageEvent
    message = MessageEvent
    

    @classmethod
    def __missing__(cls, value):
        # Define the behavior for the default member
        return cls.message
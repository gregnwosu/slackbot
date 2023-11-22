import pydantic
import datetime as dt
from typing import List, Optional
from logging import Logger
logger = Logger(__name__)

from slackbot.parsing.base.model import EventType, BlockData

class AppMentionEvent(pydantic.BaseModel):
    client_msg_id: str
    type: EventType
    text: str 
    user: str
    ts:  dt.datetime
    blocks: List[BlockData]
    team: Optional[str] 
    channel: str
    event_ts: dt.datetime
    
    @pydantic.field_validator('type')
    @classmethod
    def convert_to_event_type(cls, value):
        return EventType(value)
    




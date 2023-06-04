
import pydantic
from enum import Enum 
import datetime as dt
from typing import List, Optional

#AppMentionData


class EventType(Enum):
    APP_MENTION = "app_mention"

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


class AppMentionData(pydantic.BaseModel):
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
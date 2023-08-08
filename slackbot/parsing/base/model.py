from enum import Enum
from typing import List, Optional
import pydantic
class ChannelType(Enum):
    group = "group"
    channel = "channel"
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
    @classmethod
    def convert_to_blockelementdata_type(cls, value):
        return BlockElementDataType(value)
class BlockElement(pydantic.BaseModel):
    type: BlockElementType
    elements: List[BlockElementData]
    @pydantic.validator('type')
    @classmethod
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
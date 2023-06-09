from enum import Enum 
import pydantic
import datetime as dt
from typing import List, Optional, Dict

class MimeType(str, Enum):
    AUDIO_WEBM = "audio/webm"
    AUDIO = "audio"
    AUDIO_MP4 = "audio/mp4"
    AUDIO_MP3 = "audio/mp3"

class FileType(str, Enum):
    WEBM = "webm"
    M4A ="m4a"

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
    PROCESSING = "processing"
    NONE = "none"
class Transcription(pydantic.BaseModel):
    status: TranscriptionStatus
    locale: Optional[Locale]
    preview: Optional[Preview]

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

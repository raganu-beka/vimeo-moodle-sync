from dataclasses import dataclass
from datetime import datetime, date, time
from enum import Enum

from clients.vimeo_client.models import VimeoVideo


class TimeSource(str, Enum):
    TITLE_TIMESTAMP = 'title_timestamp'
    VIMEO_CREATED_TIME = 'vimeo_created_time'


class TitleTimestampTimezoneMode(str, Enum):
    LOCAL = 'local'
    UTC = 'utc'


@dataclass(slots=True, frozen=True)
class CourseSession:
    id: str
    type: str
    scheduled_start: datetime


@dataclass(slots=True, frozen=True)
class ParsedCourseName:
    raw: str
    course_type: str
    grade_group: str | None
    weekday: str
    start_time: time


@dataclass(slots=True, frozen=True)
class Recording:
    vimeo_video: VimeoVideo
    recording_type: str | None
    recording_start_utc: datetime
    recording_date_local: date
    time_source: TimeSource

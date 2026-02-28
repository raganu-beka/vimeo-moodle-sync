from dataclasses import dataclass
from datetime import datetime, date, time
from enum import Enum

from integrations.vimeo_client.models import VimeoVideo


class TimeSource(str, Enum):
    TITLE_TIMESTAMP = 'title_timestamp'
    VIMEO_CREATED_TIME = 'vimeo_created_time'


class TitleTimestampTimezoneMode(str, Enum):
    LOCAL = 'local'
    UTC = 'utc'


@dataclass(slots=True, frozen=True)
class CourseSession:
    course_key: str
    course_type: str
    scheduled_start_utc: datetime


@dataclass(slots=True, frozen=True)
class ParsedCourseName:
    raw: str
    course_type: str
    grade_group: str | None
    weekday: int
    start_time: time


@dataclass(slots=True, frozen=True)
class Recording:
    vimeo_video: VimeoVideo
    recording_type: str | None
    recording_start_utc: datetime
    recording_date_local: date
    time_source: TimeSource

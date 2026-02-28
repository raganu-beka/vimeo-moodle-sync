from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True, frozen=True)
class CourseSession:
    id: str
    type: str
    scheduled_start: datetime

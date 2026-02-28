import re
from abc import ABC, abstractmethod
from datetime import time, datetime
from typing import Sequence, Pattern, Mapping, Callable




class NormalizationError(Exception):
    """Thrown for any error during course name or recording name normalization"""



class CourseNameParser(ABC):
    @abstractmethod
    def parse(self, raw_name: str) -> ParsedCourseName:
        raise NotImplementedError


class RecordingTypeClassifier(ABC):
    @abstractmethod
    def classify(self, title: str) -> str:
        raise NotImplementedError


def _parse_time_value(value: str, formats: Sequence[str]) -> time:
    for fmt in formats:
        try:
            return datetime.strptime(value, fmt).time()
        except ValueError:
            continue
    raise ValueError(f'Time value \'{value}\' does not match any of the expected formats')


class RegexCourseNameParser(CourseNameParser):
    """Extracts course information from course name using regext"""

    def __init__(
            self,
            pattern: str | Pattern[str],
            group_map: Mapping[str, str],
            *,
            time_formats: Sequence[str] = ('%H%M',),
            weekday_normalizer: Callable | None = None
    ) -> None:
        self._pattern = re.compile(pattern) if isinstance(pattern, str) else pattern
        self._group_map = dict(group_map)
        self._time_formats = time_formats
        self._weekday_normalizer = weekday_normalizer or (lambda x: x)



import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import time, datetime
from enum import Enum
from typing import Sequence, Pattern, Mapping, Callable


@dataclass(slots=True, frozen=True)
class ParsedCourseName:
    raw: str
    course_type: str
    grade_group: str | None
    weekday: str
    start_time: time


class NormalizationError(Exception):
    """Thrown for any error during course name or recording name normalization"""


class UnknownTypeBehavior(str, Enum):
    RAISE = 'raise'
    RETURN_NONE = 'return_none'
    RETURN_DEFAULT = 'return_default'


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

    def parse(self, raw_name: str) -> ParsedCourseName:
        match = self._pattern.fullmatch(raw_name.strip())
        if not match:
            raise NormalizationError(f'Course name \'{raw_name}\' does not match the expected pattern')

        gd = match.groupdict()

        course_type = gd[self._group_map['course_type']]
        weekday_raw = gd[self._group_map['weekday']]
        start_time_raw = gd[self._group_map['start_time']]

        grade_group_key = self._group_map.get('grade_group')
        grade_group = gd.get(grade_group_key) if grade_group_key else None

        parsed_time = _parse_time_value(start_time_raw, self._time_formats)
        weekday = self._weekday_normalizer(weekday_raw)

        return ParsedCourseName(
            raw=raw_name,
            course_type=course_type,
            grade_group=grade_group,
            weekday=weekday,
            start_time=parsed_time
        )


class KeywordClassifier(RecordingTypeClassifier):
    """Classifies recording type based on presence of keywords (case-insensitive)"""

    def __init__(
            self,
            type_keywords: Mapping[str, Sequence[str]],
            *,
            unknown_type_behavior: UnknownTypeBehavior = UnknownTypeBehavior.RETURN_NONE,
            default_type: str | None
    ) -> None:
        self._type_keywords = {
            t: tuple(k.lower() for k in keywords)
            for t, keywords in type_keywords.items()
        }
        self._unknown_type_behavior = unknown_type_behavior
        self._default_type = default_type

    def classify(self, title: str) -> str | None:
        tokens = set(title.lower().split())

        for course_type, keywords in self._type_keywords.items():
            if any(k in tokens for k in keywords):
                return course_type

        if self._unknown_type_behavior is UnknownTypeBehavior.RETURN_NONE:
            return None
        if self._unknown_type_behavior is UnknownTypeBehavior.RETURN_DEFAULT:
            return self._default_type

        raise NormalizationError('Recording type could not be determined from title')

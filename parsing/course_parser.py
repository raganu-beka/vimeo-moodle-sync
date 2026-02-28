import re
from datetime import datetime, time
from typing import Sequence

from config import Settings
from models import ParsedCourseName
from parsing.weekday import weekday_to_int


def _parse_time_value(value: str, formats: Sequence[str]) -> time:
    for fmt in formats:
        try:
            return datetime.strptime(value, fmt).time()
        except ValueError:
            continue
    raise ValueError(f'Time value \'{value}\' does not match any of the expected formats')


def parse_course_name(raw_name: str, settings: Settings) -> ParsedCourseName:
    pattern = re.compile(settings.course_title_pattern) if isinstance(settings.course_title_pattern,
                                                                      str) else settings.course_title_pattern
    match = pattern.fullmatch(raw_name.strip())
    if not match:
        raise ValueError(f'Course name \'{raw_name}\' does not match the expected pattern')

    gd = match.groupdict()
    group_map = settings.course_title_pattern_group_map

    course_type = gd[group_map['course_type']]
    weekday_raw = gd[group_map['weekday']]
    start_time_raw = gd[group_map['start_time']]
    grade_group_key = gd[group_map['grade_group']]

    parsed_time = _parse_time_value(start_time_raw, settings.course_title_time_formats)
    weekday = weekday_to_int(weekday_raw, settings.weekday_map)

    return ParsedCourseName(
        raw=raw_name,
        course_type=course_type,
        grade_group=grade_group_key,
        weekday=weekday,
        start_time=parsed_time
    )

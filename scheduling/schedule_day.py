from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo

from models import ParsedCourseName, CourseSession


def get_sessions_for_date(
        parsed_courses: list[ParsedCourseName],
        date_local: date,
        timezone_name: str
) -> list[CourseSession]:
    local_timezone = ZoneInfo(timezone_name)
    weekday = date_local.weekday()

    date_courses = [course for course in parsed_courses if course.weekday == weekday]

    date_sessions = []
    for course in date_courses:
        course_start_local = datetime.combine(date_local, course.start_time)
        course_start_utc = course_start_local.replace(tzinfo=local_timezone).astimezone(timezone.utc)
        date_sessions.append(CourseSession(
            course_key=course.raw,
            course_type=course.course_type,
            scheduled_start_utc=course_start_utc
        ))

    return date_sessions

from datetime import date

from app.config import MoodleSettings
from app.integrations.moodle_client.models import MoodleCourseSection


def _get_section_name(
    day: date, month_aliases: dict[int, str], date_template: str
) -> str:
    month_name = month_aliases.get(day.month)
    if not month_name:
        raise ValueError(f"No month alias found for month {day.month}")

    return date_template.format(
        day=day.day,
        month_name=month_name,
    )


def get_course_section_for_day(
    sections: list[MoodleCourseSection], day: date, settings: MoodleSettings
) -> MoodleCourseSection | None:
    section_name = _get_section_name(
        day,
        settings.moodle_section_month_aliases,
        settings.moodle_section_date_template,
    )

    return next((section for section in sections if section.name == section_name), None)

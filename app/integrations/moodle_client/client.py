from typing import Any

import requests

from app.integrations.moodle_client.exceptions import MoodleError
from app.integrations.moodle_client.models import MoodleCourse, MoodleCourseSection


class MoodleClient:

    DEFAULT_TIMEOUT = 60

    def __init__(self, base_url: str, token: str) -> None:
        self.base_url = base_url
        self.token = token

    def _call(self, function_name: str, **params) -> Any:
        url = f"{self.base_url}/webservice/rest/server.php"
        payload = {
            "wstoken": self.token,
            "moodlewsrestformat": "json",
            "wsfunction": function_name,
            **params,
        }

        response = requests.post(url, data=payload, timeout=self.DEFAULT_TIMEOUT)
        response.raise_for_status()

        data = response.json()

        if isinstance(data, dict) and data.get("exception"):
            raise MoodleError(data.get("message"), data.get("errorcode"))

        return response.json()

    def get_all_courses(self) -> list[MoodleCourse]:
        data = self._call("core_course_get_courses")
        return [MoodleCourse.from_api(course) for course in data]

    def get_course_by_shortname(self, shortname: str) -> MoodleCourse | None:
        data = self._call(
            "core_course_get_courses_by_field", field="shortname", value=shortname
        )
        courses = data.get("courses", [])
        if not courses:
            return None

        course = courses[0]
        return MoodleCourse.from_api(course)

    def get_course_sections_by_shortname(
        self, shortname: str
    ) -> list[MoodleCourseSection] | None:
        course = self.get_course_by_shortname(shortname)
        if not course:
            return None

        data = self._call("core_course_get_contents", courseid=course.id)
        return [MoodleCourseSection.from_api(section) for section in data]

    def update_course_section_summary(
        self,
        section_id: int,
        summary_html: str,
        summary_format: int = 1,
    ) -> None:
        # TODO: Implement this method using to-be-developed plugin.
        pass

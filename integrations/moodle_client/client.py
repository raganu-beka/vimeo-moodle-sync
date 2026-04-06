from typing import Any

import requests

from integrations.moodle_client.exceptions import MoodleError


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

    def get_all_courses(self) -> list[dict[str, str]]:
        data = self._call("core_course_get_courses")
        return [
            {
                "id": course["id"],
                "shortname": course["shortname"],
                "fullname": course["fullname"],
            }
            for course in data
        ]

    def get_course_by_shortname(self, shortname: str) -> dict[str, str] | None:
        data = self._call(
            "core_course_get_courses_by_field", field="shortname", value=shortname
        )
        courses = data.get("courses", [])
        if not courses:
            return None

        course = courses[0]
        return {
            "id": course["id"],
            "shortname": course["shortname"],
            "fullname": course["fullname"],
        }

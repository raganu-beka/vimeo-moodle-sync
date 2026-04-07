from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class MoodleCourse:
    id: int
    shortname: str
    fullname: str

    @staticmethod
    def from_api(data: dict) -> MoodleCourse:
        return MoodleCourse(
            id=int(data["id"]),
            shortname=data["shortname"],
            fullname=data["fullname"],
        )


@dataclass(slots=True, frozen=True)
class MoodleCourseSection:
    id: int
    name: str
    summary: str

    @staticmethod
    def from_api(data: dict) -> MoodleCourseSection:
        return MoodleCourseSection(
            id=int(data["id"]),
            name=data["name"],
            summary=data["summary"],
        )

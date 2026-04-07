from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class MoodleCourse:
    id: int
    shortname: str
    fullname: str

    @staticmethod
    def from_api(data: dict):
        return MoodleCourse(
            id=int(data["id"]),
            shortname=data["shortname"],
            fullname=data["fullname"],
        )

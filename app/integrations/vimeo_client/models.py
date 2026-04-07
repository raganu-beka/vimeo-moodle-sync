from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta


@dataclass(slots=True, frozen=True)
class VimeoVideo:
    uri: str
    name: str
    link: str
    duration: timedelta
    created_time: str

    @property
    def video_id(self) -> str:
        return self.uri.rsplit("/", 1)[-1]

    @staticmethod
    def from_api(data: dict) -> VimeoVideo:
        return VimeoVideo(
            uri=data["uri"],
            name=data["name"],
            duration=timedelta(seconds=data["duration"]),
            link=data["link"],
            created_time=str(data.get("created_time")),
        )

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class VimeoVideo:
    uri: str
    name: str
    link: str
    duration: str
    created_time: Optional[str]

    @staticmethod
    def from_api(data: dict):
        return VimeoVideo(
            uri=data['uri'],
            name=data['name'],
            duration=data['duration'],
            link=data['link'],
            created_time=data.get('created_time')
        )

from typing import Any

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from course_matcher.normalize import UnknownTypeBehavior


def _get_missing_settings(required_settings: dict[str, Any]) -> list[str]:
    return [name for name, value in required_settings.items() if not value]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore'
    )

    vimeo_access_token: str = Field('VIMEO_ACCESS_TOKEN')
    vimeo_user_id: int = Field('VIMEO_USER_ID')
    vimeo_folder_id: int = Field('VIMEO_FOLDER_ID')

    course_pattern: str = Field('COURSE_PATTERN')
    group_map: dict[str, str] = Field('GROUP_MAP')
    time_formats: list[str] = Field('TIME_FORMATS')
    type_keywords: dict[str, list[str]] = Field('TYPE_KEYWORDS')
    unknown_type_behavior: str = Field(
        default=UnknownTypeBehavior.RETURN_NONE,
        alias='UNKNOWN_TYPE_BEHAVIOR'
    )
    default_type: str | None = Field('DEFAULT_TYPE')

    @field_validator('group_map')
    @classmethod
    def validate_group_map(cls, v: dict[str, str]) -> dict[str, str]:
        required_keys = {'course_type', 'weekday', 'start_time'}
        if not required_keys.issubset(v.keys()):
            missing = required_keys - v.keys()
            raise ValueError(f'GROUP_MAP is missing required keys: {missing}')
        return v

    @model_validator(mode='after')
    def validate_normalization_settings(self) -> 'Settings':
        required_settings = {
            'COURSE_PATTERN': self.course_pattern,
            'GROUP_MAP': self.group_map,
            'TIME_FORMATS': self.time_formats,
            'TYPE_KEYWORDS': self.type_keywords,
        }

        missing = _get_missing_settings(required_settings)
        if missing:
            raise ValueError(f'Missing required Vimeo settings: {missing}')

        if (
                self.unknown_type_behavior == UnknownTypeBehavior.RETURN_DEFAULT
                and not self.default_type
        ):
            raise ValueError(f'DEFAULT_TYPE is required when UNKNOWN_TYPE_BEHAVIOR is \'return_default\'')
        return self

    @model_validator(mode='after')
    def validate_vimeo_settings(self) -> 'Settings':
        required_settings = {
            'VIMEO_ACCESS_TOKEN': self.vimeo_access_token,
            'VIMEO_USER_ID': self.vimeo_user_id,
            'VIMEO_FOLDER_ID': self.vimeo_folder_id,
        }
        missing = _get_missing_settings(required_settings)
        if missing:
            raise ValueError(f'Missing required Vimeo settings: {missing}')
        return self

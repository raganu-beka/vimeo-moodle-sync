from typing import Any

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from parsing.recording_normalizer import TitleTimestampTimezoneMode


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

    timezone_name: str = Field('TIMEZONE_NAME')
    weekday_map: dict[str, int] = Field('WEEKDAY_MAP')

    courses: list[str] = Field('COURSES')
    course_title_pattern: str = Field('COURSE_TITLE_PATTERN')
    course_title_pattern_group_map: dict[str, str] = Field('COURSE_TITLE_PATTERN_GROUP_MAP')
    course_title_time_formats: list[str] = Field('COURSE_TITLE_TIME_FORMATS')

    recording_type_keywords: dict[str, list[str]] = Field('RECORDING_TYPE_KEYWORDS')
    recording_title_timestamp_pattern: str = Field('RECORDING_TITLE_TIMESTAMP_PATTERN')
    recording_title_timestamp_timezone: TitleTimestampTimezoneMode = Field('RECORDING_TITLE_TIMESTAMP_TIMEZONE')
    recording_title_timestamp_datetime_formats: list[str] = Field('RECORDING_TITLE_TIMESTAMP_DATETIME_FORMATS')

    @field_validator('course_title_pattern_group_map')
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
            'COURSES': self.courses,
            'COURSE_TITLE_PATTERN': self.course_title_pattern,
            'COURSE_TITLE_PATTERN_GROUP_MAP': self.course_title_pattern_group_map,
            'COURSE_TITLE_TIME_FORMATS': self.course_title_time_formats,
            'RECORDING_TYPE_KEYWORDS': self.recording_type_keywords,
            'RECORDING_TITLE_TIMESTAMP_PATTERN': self.recording_title_timestamp_pattern,
            'RECORDING_TITLE_TIMESTAMP_TIMEZONE': self.recording_title_timestamp_timezone,
            'RECORDING_TITLE_TIMESTAMP_DATETIME_FORMATS': self.recording_title_timestamp_datetime_formats,
            'WEEKDAY_MAP': self.weekday_map,
            'TIMEZONE_NAME': self.timezone_name,
        }
        missing = _get_missing_settings(required_settings)
        if missing:
            raise ValueError(f'Missing required parsing settings: {missing}')
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

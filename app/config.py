from functools import lru_cache
from json import load
from typing import TYPE_CHECKING

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.parsing.recording_normalizer import TitleTimestampTimezoneMode


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


class Settings(AppSettings):

    vimeo_access_token: str = Field(..., validation_alias="VIMEO_ACCESS_TOKEN")
    vimeo_user_id: int = Field(..., validation_alias="VIMEO_USER_ID")
    vimeo_folder_id: int = Field(..., validation_alias="VIMEO_FOLDER_ID")

    timezone_name: str = Field(..., validation_alias="TIMEZONE_NAME")
    weekday_map: dict[str, int] = Field(..., validation_alias="WEEKDAY_MAP")

    courses: list[str] = Field(..., validation_alias="COURSES")
    course_title_pattern: str = Field(..., validation_alias="COURSE_TITLE_PATTERN")
    course_title_pattern_group_map: dict[str, str] = Field(
        ..., validation_alias="COURSE_TITLE_PATTERN_GROUP_MAP"
    )
    course_title_time_formats: list[str] = Field(
        ..., validation_alias="COURSE_TITLE_TIME_FORMATS"
    )

    recording_type_keywords: dict[str, list[str]] = Field(
        ..., validation_alias="RECORDING_TYPE_KEYWORDS"
    )
    recording_title_timestamp_pattern: str = Field(
        ..., validation_alias="RECORDING_TITLE_TIMESTAMP_PATTERN"
    )
    recording_title_timestamp_timezone: TitleTimestampTimezoneMode = Field(
        ..., validation_alias="RECORDING_TITLE_TIMESTAMP_TIMEZONE"
    )
    recording_title_timestamp_datetime_formats: list[str] = Field(
        ..., validation_alias="RECORDING_TITLE_TIMESTAMP_DATETIME_FORMATS"
    )

    recording_early_tolerance_minutes: int = Field(
        ..., validation_alias="RECORDING_EARLY_TOLERANCE_MINUTES"
    )
    recording_late_tolerance_minutes: int = Field(
        ..., validation_alias="RECORDING_LATE_TOLERANCE_MINUTES"
    )

    if TYPE_CHECKING:

        def __init__(self) -> None: ...

    @classmethod
    @field_validator("course_title_pattern_group_map")
    def validate_group_map(cls, v: dict[str, str]) -> dict[str, str]:
        required_keys = {"course_type", "weekday", "start_time", "grade_group"}
        if not required_keys.issubset(v.keys()):
            missing = required_keys - v.keys()
            raise ValueError(f"GROUP_MAP is missing required keys: {missing}")
        return v


class VideoUpdateSettings(AppSettings):
    video_settings_file: str = Field(..., validation_alias="VIDEO_SETTINGS_FILE")
    video_settings_name_field: str = Field(
        ..., validation_alias="VIDEO_SETTINGS_NAME_FIELD"
    )
    video_name_timestamp_format: str = Field(
        ..., validation_alias="VIDEO_NAME_TIMESTAMP_FORMAT"
    )

    if TYPE_CHECKING:

        def __init__(self) -> None: ...


class MoodleSettings(AppSettings):
    moodle_base_url: str = Field(..., validation_alias="MOODLE_BASE_URL")
    moodle_access_token: str = Field(..., validation_alias="MOODLE_ACCESS_TOKEN")
    moodle_section_date_template: str = Field(
        ..., validation_alias="MOODLE_SECTION_DATE_TEMPLATE"
    )
    moodle_section_month_aliases: dict[int, str] = Field(
        ..., validation_alias="MOODLE_SECTION_MONTH_ALIASES"
    )

    if TYPE_CHECKING:

        def __init__(self) -> None: ...


@lru_cache
def get_settings() -> Settings:
    return Settings()


@lru_cache
def get_video_update_settings() -> VideoUpdateSettings:
    return VideoUpdateSettings()


@lru_cache
def get_moodle_settings() -> MoodleSettings:
    return MoodleSettings()


@lru_cache
def load_settings_from_json(filepath: str) -> dict:
    with open(filepath, "r", encoding="utf-8") as settings_file:
        return load(settings_file)

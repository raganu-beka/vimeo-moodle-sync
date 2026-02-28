import re
from datetime import datetime, timezone
from typing import Pattern, Sequence
from zoneinfo import ZoneInfo

import config
from clients.vimeo_client.models import VimeoVideo
from course_matcher.models import TitleTimestampTimezoneMode, TimeSource, Recording


def _extract_title_timestamp(
        title: str,
        pattern: Pattern[str] | str,
        datetime_formats: Sequence[str] = ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M')
) -> datetime | None:
    pattern = re.compile(pattern) if isinstance(pattern, str) else pattern
    match = pattern.search(title)

    if not match:
        return None

    timestamp = f'{match.group('date')} {match.group('time')}'
    for fmt in datetime_formats:
        try:
            return datetime.strptime(timestamp, fmt)
        except ValueError:
            continue

    return None


def _classify_recording_type(
        title: str,
        type_keywords: dict[str, list[str]]
) -> str | None:
    tokens = title.lower().split()

    for t, keywords in type_keywords.items():
        if any(keyword in tokens for keyword in keywords):
            return t

    return None


def _parse_vimeo_created_time(created_time: str) -> datetime:
    dt = datetime.fromisoformat(created_time.replace('Z', '+00:00'))
    return dt.astimezone(timezone.utc)


def normalize_recording(vimeo_video: VimeoVideo, settings: config.Settings) -> Recording:
    local_timezone = ZoneInfo(settings.timezone_name)
    title_timestamp = _extract_title_timestamp(
        vimeo_video.name,
        settings.recording_title_timestamp_pattern,
        settings.recording_title_timestamp_datetime_formats)

    if title_timestamp is not None:
        time_source = TimeSource.TITLE_TIMESTAMP
        if settings.recording_title_timestamp_timezone == TitleTimestampTimezoneMode.UTC:
            recording_start_utc = title_timestamp.replace(tzinfo=timezone.utc).astimezone(timezone.utc)
        else:
            recording_start_utc = title_timestamp.replace(tzinfo=local_timezone).astimezone(timezone.utc)


    else:
        time_source = TimeSource.VIMEO_CREATED_TIME
        recording_start_utc = _parse_vimeo_created_time(vimeo_video.created_time)

    recording_type = _classify_recording_type(vimeo_video.name, settings.recording_type_keywords)
    recording_date_local = recording_start_utc.astimezone(local_timezone).date()

    return Recording(
        vimeo_video=vimeo_video,
        recording_type=recording_type,
        recording_start_utc=recording_start_utc,
        recording_date_local=recording_date_local,
        time_source=time_source,
    )

from datetime import timedelta, datetime
from typing import Any
from models import CourseSession, Recording


def _get_sorted_by_key(list_items: list[Any], key: str) -> list[Any]:
    return sorted(list_items, key=lambda x: getattr(x, key))


def _get_grouped_by_key(list_items: list[Any], key: str) -> dict[Any, list[Any]]:
    grouped_by_key = {}
    for item in list_items:
        grouped_by_key.setdefault(getattr(item, key), []).append(item)

    return grouped_by_key


def _is_within_early_tolerance(session_start: datetime,
                               recording_start: datetime,
                               early_tolerance: timedelta) -> bool:
    return session_start - early_tolerance <= recording_start


def _is_within_late_tolerance(session_start: datetime,
                              recording_start: datetime,
                              late_tolerance: timedelta) -> bool:
    return recording_start <= session_start + late_tolerance


def get_sessions_by_type(sessions: list[CourseSession]) -> dict[str, list[CourseSession]]:
    sessions_by_type = _get_grouped_by_key(sessions, 'course_type')
    for key, value in sessions_by_type.items():
        sessions_by_type[key] = _get_sorted_by_key(value, 'scheduled_start_utc')

    return sessions_by_type


def get_recordings_by_type(recordings: list[Recording]) -> dict[str, list[Recording]]:
    recordings_by_type = _get_grouped_by_key(recordings, 'recording_type')
    for key, value in recordings_by_type.items():
        recordings_by_type[key] = _get_sorted_by_key(value, 'recording_start_utc')

    return recordings_by_type


def _get_session_recording_candidates(sessions_by_type: dict[str, list[CourseSession]],
                                      recordings_by_type: dict[str, list[Recording]],
                                      *,
                                      early_tolerance: timedelta = timedelta(minutes=15),
                                      late_tolerance: timedelta = timedelta(minutes=15)):
    candidates: dict[str, list[Recording]] = dict()
    for session_type in sessions_by_type.keys():
        if not session_type:
            continue

        sessions = sessions_by_type[session_type]
        recordings = recordings_by_type.get(session_type, [])

        i = 0
        for session in sessions:
            while i < len(recordings):
                if not _is_within_late_tolerance(session.scheduled_start_utc, recordings[i].recording_start_utc,
                                                 late_tolerance):
                    break

                if _is_within_early_tolerance(session.scheduled_start_utc, recordings[i].recording_start_utc,
                                              early_tolerance):
                    candidates.setdefault(session.course_key, []).append(recordings[i])

                i += 1

    return candidates


def _get_matches_from_candidates(recording_candidates: dict[str, list[Recording]]) -> dict[str, Recording]:
    matches: dict[str, Recording] = dict()
    for course_key, recordings in recording_candidates.items():
        longest = max(recordings, key=lambda x: x.vimeo_video.duration)
        matches[course_key] = longest

    return matches


def match_session_recordings(sessions: list[CourseSession],
                            recordings: list[Recording],
                            *,
                            early_tolerance: timedelta = timedelta(minutes=15),
                            late_tolerance: timedelta = timedelta(minutes=15)) -> dict[str, Recording]:
    sessions_by_type = get_sessions_by_type(sessions)
    recordings_by_type = get_recordings_by_type(recordings)
    candidates = _get_session_recording_candidates(sessions_by_type, recordings_by_type,
                                                   early_tolerance=early_tolerance,
                                                   late_tolerance=late_tolerance)
    return _get_matches_from_candidates(candidates)

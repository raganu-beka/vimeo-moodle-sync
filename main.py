from datetime import datetime, UTC
from pprint import pprint
from json import load
import argparse

import config
from integrations.vimeo_client import VimeoClient
from matching.match_session_recordings import match_session_recordings
from parsing.course_parser import parse_course_name
from parsing.recording_normalizer import normalize_recording
from scheduling.schedule_day import get_sessions_for_date


def load_settings_from_json(filepath: str) -> dict:
    with open(filepath, 'r', encoding='utf-8') as settings_file:
        return load(settings_file)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--day',
        nargs='?',
        type=lambda x: datetime.strptime(x, '%Y-%m-%d').date(),
        default=datetime.now(UTC).date(),
        help='Date to get match recordings for in YYYY-MM-DD format. Defaults to current UTC day.'
    )
    args = parser.parse_args()

    settings = config.Settings()
    vimeo = VimeoClient(settings.vimeo_access_token)

    videos = vimeo.get_user_folder_videos_by_date(settings.vimeo_user_id, settings.vimeo_folder_id, args.day)

    courses = [parse_course_name(course, settings) for course in settings.courses]
    sessions = get_sessions_for_date(courses, args.day, settings.timezone_name)
    recordings = [normalize_recording(video, settings) for video in videos]

    match_result = match_session_recordings(sessions, recordings, settings)
    pprint(match_result)

    video_settings = load_settings_from_json(settings.video_settings_file)

    for course_name, recording in match_result.matches.items():
        recording_name = f'{course_name}-{args.day.strftime(settings.video_name_timestamp_format)}'

        recording_settings = video_settings.copy()
        recording_settings[settings.video_settings_name_field] = recording_name

        print(f'Updating settings for recording \'{recording.vimeo_video.name}\' ({recording_name})')
        vimeo.update_video_settings(recording.vimeo_video.uri, recording_settings)

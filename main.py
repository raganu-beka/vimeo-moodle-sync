from datetime import datetime, UTC
from pprint import pprint
import argparse

import config
from integrations.vimeo_client import VimeoClient
from matching.match_session_recordings import match_session_recordings
from parsing.course_parser import parse_course_name
from parsing.recording_normalizer import normalize_recording
from scheduling.schedule_day import get_sessions_for_date

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

    pprint(match_session_recordings(sessions, recordings, settings))
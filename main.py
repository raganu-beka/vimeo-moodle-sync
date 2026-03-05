from datetime import date
from pprint import pprint

import config
from integrations.vimeo_client import VimeoClient
from matching.match_session_recordings import get_sessions_by_type, get_recordings_by_type, match_session_recordings
from parsing.course_parser import parse_course_name
from parsing.recording_normalizer import normalize_recording
from scheduling.schedule_day import get_sessions_for_date

if __name__ == '__main__':

    settings = config.Settings()

    vimeo = VimeoClient(settings.vimeo_access_token)

    day = date(2026, 3, 5)
    videos = vimeo.get_user_folder_videos_by_date(settings.vimeo_user_id, settings.vimeo_folder_id, day)

    courses = [parse_course_name(course, settings) for course in settings.courses]
    sessions = get_sessions_for_date(courses, day, settings.timezone_name)
    recordings = [normalize_recording(video, settings) for video in videos]

    sessions_by_type = get_sessions_by_type(sessions)
    recordings_by_type = get_recordings_by_type(recordings)

    pprint(match_session_recordings(sessions, recordings))
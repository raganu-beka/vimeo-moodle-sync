from datetime import date
from pprint import pprint

import config
from integrations.vimeo_client import VimeoClient
from parsing.course_parser import parse_course_name
from parsing.recording_normalizer import normalize_recording
from scheduling.schedule_day import get_sessions_for_date

settings = config.Settings()

vimeo = VimeoClient(settings.vimeo_access_token)

day = date(2026, 2, 26)
videos = vimeo.get_user_folder_videos_by_date(settings.vimeo_user_id, settings.vimeo_folder_id, day)

parsed_course_names = [parse_course_name(course, settings) for course in settings.courses]
sessions = get_sessions_for_date(parsed_course_names, day, settings.timezone_name)
pprint(sessions)

for video in videos:
    normalized_recording = normalize_recording(video, settings)
    pprint(normalized_recording)

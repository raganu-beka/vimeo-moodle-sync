from datetime import date
from pprint import pprint

import config
from clients.vimeo_client import VimeoClient
from course_matcher.parsing.course_parser import parse_course_name
from course_matcher.parsing.recording_normalizer import normalize_recording

settings = config.Settings()

vimeo = VimeoClient(settings.vimeo_access_token)

day = date(2026, 2, 26)
videos = vimeo.get_user_folder_videos_by_date(settings.vimeo_user_id, settings.vimeo_folder_id, day)
pprint(videos)

parsed_course_name = parse_course_name("Dat-8-Thu-1200", settings)
pprint(parsed_course_name)

for video in videos:
    normalized_recording = normalize_recording(video, settings)
    pprint(normalized_recording)

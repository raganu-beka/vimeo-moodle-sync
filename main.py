from datetime import date
from pprint import pprint

import config
from clients.vimeo_client import VimeoClient
from course_matcher.normalize import RegexCourseNameParser, KeywordClassifier

settings = config.Settings()

vimeo = VimeoClient(settings.vimeo_access_token)

day = date(2026, 2, 26)
videos = vimeo.get_user_folder_videos_by_date(settings.vimeo_user_id, settings.vimeo_folder_id, day)
pprint(videos)

parser = RegexCourseNameParser(
    pattern=settings.course_pattern,
    group_map=settings.group_map,
    time_formats=settings.time_formats,
)

classifier = KeywordClassifier(type_keywords=settings.type_keywords)

parsed_course_name = parser.parse("Dat-8-Thu-1200")
pprint(parsed_course_name)

for video in videos:
    course_name = video.name
    try:
        recording_type = classifier.classify(course_name)
        print(f"Video '{course_name}' is classified as '{recording_type}'")
    except Exception as e:
        print(f"Failed to parse video name '{course_name}': {e}")

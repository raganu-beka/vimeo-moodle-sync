from datetime import date
from pprint import pprint

import config
from clients.vimeo_client import VimeoClient

vimeo = VimeoClient(config.VIMEO_ACCESS_TOKEN)

day = date(2026, 2, 26)
videos = vimeo.get_user_folder_videos_by_date(config.VIMEO_USER_ID, config.VIMEO_FOLDER_ID, day)
pprint(videos)

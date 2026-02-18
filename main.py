from pprint import pprint

import config
from clients.vimeo_client import VimeoClient

vimeo = VimeoClient(config.VIMEO_ACCESS_TOKEN)

today_videos = vimeo.get_user_folder_today_videos(config.VIMEO_USER_ID, config.VIMEO_FOLDER_ID)
pprint(today_videos)

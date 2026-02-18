import config

from clients.vimeo_client import VimeoClient

vimeo = VimeoClient(config.VIMEO_ACCESS_TOKEN)
print(vimeo.get_me())

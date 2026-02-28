from datetime import datetime, date

import vimeo

from .models import VimeoVideo


class VimeoClient:
    MAX_RESULTS = 25

    def __init__(self, access_token: str) -> None:
        self.client = vimeo.client.VimeoClient(token=access_token)

    def get_me(self) -> dict:
        response = self.client.get('/me')
        response.raise_for_status()
        return response.json()

    def get_user_folder(self, user_id: int, folder_id: int) -> dict:
        response = self.client.get(f'/users/{user_id}/projects/{folder_id}')
        response.raise_for_status()
        return response.json()

    def get_user_folder_videos(self, user_id: int, folder_id: int, query_params: str = None) -> dict:
        request_uri = f'/users/{user_id}/projects/{folder_id}/videos'
        if query_params:
            request_uri += f'?{query_params}'

        response = self.client.get(request_uri)
        response.raise_for_status()
        return response.json()

    def get_user_folder_videos_by_date(self, user_id: int, folder_id: int, day: date) -> list[VimeoVideo]:
        request_params = f'sort=date&direction=desc&per_page={VimeoClient.MAX_RESULTS}&filter_content=videos'
        videos = self.get_user_folder_videos(user_id, folder_id, request_params)

        videos_on_day = []
        for video in videos['data']:
            created_time = video['created_time']
            video_date = datetime.fromisoformat(created_time).date()

            if video_date == day:
                videos_on_day.append(VimeoVideo.from_api(video))

        return videos_on_day

import vimeo


class VimeoClient:
    def __init__(self, access_token):
        self.client = vimeo.client.VimeoClient(token=access_token)

    def get_me(self):
        response = self.client.get('/me')
        response.raise_for_status()
        return response.json()

    def get_folder_video(self):
        pass

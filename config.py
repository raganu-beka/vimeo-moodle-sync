import os

import dotenv

dotenv.load_dotenv()

VIMEO_ACCESS_TOKEN = os.getenv("VIMEO_ACCESS_TOKEN")
if not VIMEO_ACCESS_TOKEN:
    raise ValueError("VIMEO_ACCESS_TOKEN is not set in the environment variables.")

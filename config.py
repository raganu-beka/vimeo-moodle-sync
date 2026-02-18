import os

import dotenv

dotenv.load_dotenv()


def _get_required_str_env(var_name: str) -> str:
    value = os.getenv(var_name)
    if value is None:
        raise ValueError(f"{var_name} is not set.")
    return value


def _get_required_int_env(var_name: str) -> int:
    value = _get_required_str_env(var_name)
    try:
        return int(value)
    except ValueError:
        raise ValueError(f"{var_name} must be a valid integer, got '{value}'")


VIMEO_ACCESS_TOKEN = _get_required_str_env("VIMEO_ACCESS_TOKEN")
VIMEO_USER_ID = _get_required_int_env("VIMEO_USER_ID")
VIMEO_FOLDER_ID = _get_required_int_env("VIMEO_FOLDER_ID")

import app.config as config
from app.integrations.vimeo_client.models import VimeoVideo


def get_video_embed(recording: VimeoVideo, recording_title: str) -> str:
    configuration = config.get_video_update_settings().video_embed_configuration
    template = config.load_video_embed_template_from_file()

    return template.format(
        video_id=recording.video_id,
        title=recording_title,
        max_width=configuration["max_width"],
        width=configuration["width"],
        height=configuration["height"],
    )


def append_embed_to_summary(existing_summary: str, embed_html: str) -> str:
    existing_summary = existing_summary.strip()
    embed_html = embed_html.strip()

    if embed_html in existing_summary:
        return existing_summary

    if not existing_summary:
        return embed_html

    return f"{existing_summary}\n<br>\n{embed_html}"

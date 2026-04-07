import argparse
from datetime import UTC, date, datetime

import app.config as config
from app.embedding.embed_video import append_embed_to_summary, get_video_embed
from app.integrations.moodle_client import MoodleClient
from app.integrations.vimeo_client import VimeoClient
from app.integrations.vimeo_client.models import VimeoVideo
from app.matching.match_date_section import get_course_section_for_day
from app.matching.match_session_recordings import match_session_recordings
from app.models import MatchResult
from app.parsing.course_parser import parse_course_name
from app.parsing.recording_normalizer import normalize_recording
from app.scheduling.schedule_day import get_sessions_for_date


def update_moodle_course_section(
    recording: VimeoVideo, recording_title: str, course_name: str, day: date
) -> None:
    moodle_settings = config.get_moodle_settings()

    moodle = MoodleClient(
        moodle_settings.moodle_base_url, moodle_settings.moodle_access_token
    )
    course_sections = moodle.get_course_sections_by_shortname(course_name)
    if not course_sections:
        raise Exception(f"Failed to fetch course data for '{course_name}'")

    day_section = get_course_section_for_day(course_sections, day, moodle_settings)
    if not day_section:
        raise Exception(
            f"Failed to find section for {day.strftime("%d-%m-%Y")} in course '{course_name}'"
        )

    embed_html = get_video_embed(recording, recording_title)
    updated_summary = append_embed_to_summary(day_section.summary, embed_html)

    try:
        moodle.update_course_section_summary(day_section.id, updated_summary)
    except Exception as e:
        raise Exception(
            f"Error publishing recording '{recording.name}' ('{recording_title}')", e
        )


def update_recording_settings(recording: VimeoVideo, recording_title: str) -> None:
    settings = config.get_settings()
    video_update_settings = config.get_video_update_settings()

    recording_settings = config.load_video_update_settings_from_file().copy()
    recording_settings[video_update_settings.video_settings_name_field] = (
        recording_title
    )

    vimeo = VimeoClient(settings.vimeo_access_token)

    try:
        vimeo.update_video_settings(recording, recording_settings)
    except Exception as e:
        raise Exception(
            f"Error updating settings for recording '{recording.name}' ('{recording_title}')",
            e,
        )

    try:
        vimeo.set_random_thumbnail_for_video(recording)
    except Exception as e:
        raise Exception(
            f"Error setting thumbnail for recording '{recording.name}' ('{recording_title}')",
            e,
        )


def get_recording_title(course_name: str, day: date):
    video_update_settings = config.get_video_update_settings()
    return f"{course_name}-{day.strftime(video_update_settings.video_name_timestamp_format)}"


def match_session_recordings_for_day(day: date) -> MatchResult:
    settings = config.get_settings()

    vimeo = VimeoClient(settings.vimeo_access_token)
    videos = vimeo.get_user_folder_videos_by_date(
        settings.vimeo_user_id, settings.vimeo_folder_id, day
    )

    courses = [parse_course_name(course, settings) for course in settings.courses]
    sessions = get_sessions_for_date(courses, day, settings.timezone_name)
    recordings = [normalize_recording(video, settings) for video in videos]

    return match_session_recordings(sessions, recordings, settings)


def print_match_result(match_result: MatchResult) -> None:
    matched_headers = ("Matched Recording", "Matched Course")
    matched_rows = [
        (recording.vimeo_video.name, course_name)
        for course_name, recording in match_result.matches.items()
    ]

    matched_widths = (
        max(
            [len(matched_headers[0]), *[len(row[0]) for row in matched_rows]],
            default=len(matched_headers[0]),
        ),
        max(
            [len(matched_headers[1]), *[len(row[1]) for row in matched_rows]],
            default=len(matched_headers[1]),
        ),
    )

    def print_recording_list(title: str, recordings: list) -> None:
        print(f"\n{title}:")
        if not recordings:
            print("  - none")
            return

        for recording in recordings:
            print(f"  - {recording.vimeo_video.name}")

    header = f"{matched_headers[0]:<{matched_widths[0]}} | {matched_headers[1]:<{matched_widths[1]}}"
    separator = f'{"-" * matched_widths[0]}-+-{"-" * matched_widths[1]}'

    print(header)
    print(separator)
    if matched_rows:
        for recording_name, course_name in matched_rows:
            print(
                f"{recording_name:<{matched_widths[0]}} | {course_name:<{matched_widths[1]}}"
            )
    else:
        print("No matched recordings.")

    print_recording_list("Unmatched recordings", match_result.unmatched)
    print_recording_list(
        "Unmatched recordings with no candidate", match_result.unmatched_no_candidate
    )
    print_recording_list("Candidates not selected", match_result.candidate_not_selected)


def run_integration() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--day",
        nargs="?",
        type=lambda x: datetime.strptime(x, "%Y-%m-%d").date(),
        default=datetime.now(UTC).date(),
        help="Date to get match recordings for in YYYY-MM-DD format. Defaults to current UTC day.",
    )
    parser.add_argument(
        "--auto-accept-prompts",
        action="store_true",
        help="Skip interactive confirmation prompts and accept them automatically.",
    )
    args = parser.parse_args()

    match_result = match_session_recordings_for_day(args.day)
    print_match_result(match_result)

    if not match_result.matches:
        return

    if not args.auto_accept_prompts:
        change_settings_input = input(
            "Do you wish to update settings for matched recordings? (Y/n): "
        )
        if change_settings_input != "Y":
            print("Exiting without updating settings.")
            return

    for course_name, recording in match_result.matches.items():

        try:
            recording_title = get_recording_title(course_name, args.day)

            print(
                f"Updating Vimeo settings for recording '{recording.vimeo_video.name}' ('{recording_title}')"
            )
            # update_recording_settings(recording, recording_title)
            print(f"Publishing recording '{recording_title}' to course {course_name}")
            update_moodle_course_section(
                recording.vimeo_video, recording_title, course_name, args.day
            )

        except Exception as e:
            print(f"Error processing recording '{recording.vimeo_video.name}': {e}")


if __name__ == "__main__":
    run_integration()

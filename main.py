import argparse
from datetime import UTC, datetime
from json import load

import config
from integrations.vimeo_client import VimeoClient
from matching.match_session_recordings import match_session_recordings
from models import MatchResult
from parsing.course_parser import parse_course_name
from parsing.recording_normalizer import normalize_recording
from scheduling.schedule_day import get_sessions_for_date


def load_settings_from_json(filepath: str) -> dict:
    with open(filepath, "r", encoding="utf-8") as settings_file:
        return load(settings_file)


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

    settings = config.Settings()
    vimeo = VimeoClient(settings.vimeo_access_token)

    videos = vimeo.get_user_folder_videos_by_date(
        settings.vimeo_user_id, settings.vimeo_folder_id, args.day
    )

    courses = [parse_course_name(course, settings) for course in settings.courses]
    sessions = get_sessions_for_date(courses, args.day, settings.timezone_name)
    recordings = [normalize_recording(video, settings) for video in videos]

    match_result = match_session_recordings(sessions, recordings, settings)
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

    video_settings = load_settings_from_json(settings.video_settings_file)

    for course_name, recording in match_result.matches.items():
        recording_name = (
            f"{course_name}-{args.day.strftime(settings.video_name_timestamp_format)}"
        )

        recording_settings = video_settings.copy()
        recording_settings[settings.video_settings_name_field] = recording_name

        print(
            f"Updating settings for recording '{recording.vimeo_video.name}' ({recording_name})"
        )

        vimeo.update_video_settings(recording.vimeo_video, recording_settings)
        vimeo.set_random_thumbnail_for_video(recording.vimeo_video)


if __name__ == "__main__":
    run_integration()

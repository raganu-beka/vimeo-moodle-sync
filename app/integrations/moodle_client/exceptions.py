class MoodleError(RuntimeError):
    def __init__(self, message: str | None, error_code: str | None):
        super().__init__(f"Moodle API error {error_code or ""}: {message or "unknown"}")

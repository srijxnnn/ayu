from datetime import UTC, datetime

REMINDER_SECONDS = 3600
REMINDER_TOLERANCE = 60


def seconds_until_start(start_time_seconds: int) -> int:
    now = datetime.now(UTC).timestamp()
    return int(start_time_seconds - now)


def is_reminder_due(start_time_seconds: int) -> bool:
    delta = seconds_until_start(start_time_seconds)
    return (
        REMINDER_SECONDS - REMINDER_TOLERANCE
        <= delta
        <= REMINDER_SECONDS + REMINDER_TOLERANCE
    )


def contest_url(contest_id: int) -> str:
    return f"https://codeforces.com/contests/{contest_id}"


def contest_reminder_message(contest: dict, role_mention: str) -> str:
    name = contest["name"]
    url = contest_url(contest["id"])

    return (
        f"**contest reminder**\n\n**{name}** starts in 1 hour!\n{url}\n\n{role_mention}"
    )

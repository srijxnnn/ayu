import discord

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


def role_ping_mentions(role: discord.Role) -> discord.AllowedMentions:
    return discord.AllowedMentions(roles=[role])


def contest_url(contest_id: int) -> str:
    return f"https://codeforces.com/contests/{contest_id}"


def format_contest_start(start_time_seconds: int) -> str:
    dt = datetime.fromtimestamp(start_time_seconds, tz=UTC)
    return discord.utils.format_dt(dt, style="F")


def format_time_until(start_time_seconds: int) -> str:
    dt = datetime.fromtimestamp(start_time_seconds, tz=UTC)
    return discord.utils.format_dt(dt, style="R")


def format_upcoming_contests(contests: list[dict], *, limit: int = 5) -> str:
    lines = ["**upcoming contests**\n"]

    for contest in contests[:limit]:
        name = contest["name"]
        url = contest_url(contest["id"])
        start = contest["startTimeSeconds"]
        lines.append(
            f"**{name}**\n"
            f"starts: {format_contest_start(start)} ({format_time_until(start)})\n"
            f"{url}\n"
        )

    return "\n".join(lines).rstrip()


def contest_reminder_message(contest: dict, role_mention: str) -> str:
    name = contest["name"]
    url = contest_url(contest["id"])

    return (
        f"**contest reminder**\n\n**{name}** starts in 1 hour!\n{url}\n\n{role_mention}"
    )

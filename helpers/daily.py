import re
import sqlite3
from datetime import date, datetime

from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

DEFAULT_TIMEZONE = "Asia/Kolkata"
DEFAULT_MIN_RATING = 1000
DEFAULT_MAX_RATING = 1400
LEADERBOARD_PAGE_SIZE = 10

TIME_PATTERN = re.compile(r"^([01]?\d|2[0-3]):([0-5]\d)$")


def parse_time(time: str) -> tuple[int, int] | None:
    match = TIME_PATTERN.match(time)
    if not match:
        return None
    return int(match.group(1)), int(match.group(2))


def validate_rating_range(min_rating: int, max_rating: int) -> str | None:
    for label, rating in (("min", min_rating), ("max", max_rating)):
        if rating < 800 or rating > 3500 or rating % 100 != 0:
            return f"{label} rating must be a multiple of 100 between 800 and 3500."
    if min_rating > max_rating:
        return "min rating cannot be greater than max rating."
    return None


def validate_timezone(timezone: str) -> str | None:
    try:
        ZoneInfo(timezone)
    except ZoneInfoNotFoundError:
        return f"unknown timezone `{timezone}`. example: `Asia/Kolkata`, `UTC`."
    return None


def format_rating_value(min_rating: int, max_rating: int) -> str:
    if min_rating == max_rating:
        return f"**{min_rating}**"
    return f"**{min_rating}-{max_rating}**"


def format_rating_phrase(min_rating: int, max_rating: int) -> str:
    word = "rating" if min_rating == max_rating else "ratings"
    return f"{word} {format_rating_value(min_rating, max_rating)}"


def now_in_timezone(timezone: str) -> datetime:
    return datetime.now(ZoneInfo(timezone))


def today_in_timezone(timezone: str) -> date:
    return now_in_timezone(timezone).date()


def today_iso(timezone: str) -> str:
    return today_in_timezone(timezone).isoformat()


def effective_daily_streak(
    streak: int,
    last_completed_date: str | None,
    timezone: str,
) -> int:
    if not last_completed_date:
        return 0

    today = today_in_timezone(timezone)
    last = date.fromisoformat(last_completed_date)
    days_since = (today - last).days
    if days_since <= 1:
        return streak
    return 0


def is_scheduled_now(config: sqlite3.Row) -> bool:
    try:
        now = now_in_timezone(config["timezone"])
    except Exception:
        return False
    return now.hour == config["hour"] and now.minute == config["minute"]


def problem_url(contest_id: int, problem_index: str) -> str:
    return f"https://codeforces.com/problemset/problem/{contest_id}/{problem_index}"


def build_daily_leaderboard_entries(
    rows: list[sqlite3.Row],
    timezone: str,
) -> list[tuple[str, int]]:
    entries: list[tuple[str, int]] = []
    for row in rows:
        streak = effective_daily_streak(
            row["streak"],
            row["last_completed_date"],
            timezone,
        )
        entries.append((row["cf_handle"], streak))
    entries.sort(key=lambda entry: (-entry[1], entry[0].lower()))
    return entries


def format_daily_leaderboard(
    entries: list[tuple[str, int]],
    *,
    page: int,
    page_size: int = LEADERBOARD_PAGE_SIZE,
) -> str:
    if not entries:
        return "no one has a daily streak yet."

    start = (page - 1) * page_size
    page_entries = entries[start : start + page_size]
    if not page_entries:
        total_pages = (len(entries) + page_size - 1) // page_size
        return (
            f"page **{page}** is empty "
            f"(there are **{total_pages}** page{'s' if total_pages != 1 else ''})."
        )

    lines = [f"**daily streak leaderboard** (page {page})\n"]
    for rank, (handle, streak) in enumerate(page_entries, start=start + 1):
        day_word = "day" if streak == 1 else "days"
        lines.append(f"**{rank}.** {handle} - **{streak}** {day_word}")
    return "\n".join(lines)


def daily_problem_message(problem: sqlite3.Row) -> str:
    rating = problem["rating"] if problem["rating"] is not None else "?"
    contest_id = problem["contest_id"]
    problem_index = problem["problem_index"]
    url = problem_url(contest_id, problem_index)

    return (
        f"**daily practice problem**\n\n"
        f"**{contest_id}{problem_index} - {problem['name']}**\n"
        f"rating: {rating}\n"
        f"{url}\n"
        f"_solve it and run `;daily done` when finished!_"
    )

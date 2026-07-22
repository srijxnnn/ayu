import re
import sqlite3
from datetime import date, datetime

from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

DEFAULT_TIMEZONE = "Asia/Kolkata"
DEFAULT_MIN_RATING = 1000
DEFAULT_MAX_RATING = 1400

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


def is_scheduled_now(config: sqlite3.Row) -> bool:
    try:
        now = now_in_timezone(config["timezone"])
    except Exception:
        return False
    return now.hour == config["hour"] and now.minute == config["minute"]


def problem_url(contest_id: int, problem_index: str) -> str:
    return f"https://codeforces.com/problemset/problem/{contest_id}/{problem_index}"


def daily_problem_message(problem: sqlite3.Row) -> str:
    rating = problem["rating"] if problem["rating"] is not None else "?"
    contest_id = problem["contest_id"]
    problem_index = problem["problem_index"]
    url = problem_url(contest_id, problem_index)

    return (
        f"**daily practice problem - {contest_id}{problem_index}**\n"
        f"**{problem['name']}**\n"
        f"rating: {rating}\n"
        f"{url}\n"
        f"_solve it and share your approach!_"
    )

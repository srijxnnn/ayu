import sqlite3

from db.connection import connect

_CONFIG_ID = 1


def get_daily_config() -> sqlite3.Row | None:
    with connect() as conn:
        return conn.execute(
            """
            SELECT channel_id, hour, minute, timezone,
                   min_rating, max_rating, enabled
            FROM daily_problem_config
            WHERE id = ?
            """,
            (_CONFIG_ID,),
        ).fetchone()


def upsert_daily_config(
    *,
    channel_id: int,
    hour: int,
    minute: int,
    timezone: str = "Asia/Kolkata",
    min_rating: int = 1000,
    max_rating: int = 1400,
) -> None:
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO daily_problem_config (
                id, channel_id, hour, minute, timezone,
                min_rating, max_rating, enabled
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, 1)
            ON CONFLICT(id) DO UPDATE SET
                channel_id = excluded.channel_id,
                hour = excluded.hour,
                minute = excluded.minute,
                timezone = excluded.timezone,
                min_rating = excluded.min_rating,
                max_rating = excluded.max_rating,
                enabled = 1
            """,
            (_CONFIG_ID, channel_id, hour, minute, timezone, min_rating, max_rating),
        )


def update_daily_timezone(timezone: str) -> bool:
    with connect() as conn:
        cur = conn.execute(
            """
            UPDATE daily_problem_config
            SET timezone = ?
            WHERE id = ?
            """,
            (timezone, _CONFIG_ID),
        )
        return cur.rowcount > 0


def disable_daily_config() -> bool:
    with connect() as conn:
        cur = conn.execute(
            """
            UPDATE daily_problem_config
            SET enabled = 0
            WHERE id = ?
            """,
            (_CONFIG_ID,),
        )
        return cur.rowcount > 0


def already_posted_today(posted_date: str) -> bool:
    with connect() as conn:
        row = conn.execute(
            """
            SELECT 1
            FROM daily_problems_posted
            WHERE posted_date = ?
            """,
            (posted_date,),
        ).fetchone()
        return row is not None


def record_daily_post(
    posted_date: str,
    contest_id: int,
    problem_index: str,
) -> None:
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO daily_problems_posted (
                posted_date, contest_id, problem_index
            )
            VALUES (?, ?, ?)
            ON CONFLICT(posted_date) DO UPDATE SET
                contest_id = excluded.contest_id,
                problem_index = excluded.problem_index
            """,
            (posted_date, contest_id, problem_index),
        )


def pick_daily_problem(
    *,
    min_rating: int,
    max_rating: int,
    exclude_days: int = 30,
) -> sqlite3.Row | None:
    with connect() as conn:
        return conn.execute(
            """
            SELECT p.contest_id, p.problem_index, p.name, p.rating, p.tags
            FROM problems p
            WHERE p.rating BETWEEN ? AND ?
              AND NOT EXISTS (
                  SELECT 1
                  FROM daily_problems_posted d
                  WHERE d.contest_id = p.contest_id
                    AND d.problem_index = p.problem_index
                    AND d.posted_date >= date('now', ?)
              )
            ORDER BY RANDOM()
            LIMIT 1
            """,
            (min_rating, max_rating, f"-{exclude_days} days"),
        ).fetchone()

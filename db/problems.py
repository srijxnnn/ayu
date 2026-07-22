import sqlite3

from db.connection import connect
from db.users import get_verified_user


def upsert_problems(problems: list[tuple[int, str, str, int | None, str]]) -> int:
    with connect() as conn:
        conn.executemany(
            """
            INSERT INTO problems (contest_id, problem_index, name, rating, tags)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(contest_id, problem_index) DO UPDATE SET
                name = excluded.name,
                rating = excluded.rating,
                tags = excluded.tags
            """,
            problems,
        )
        count = conn.execute("SELECT COUNT(*) FROM problems").fetchone()[0]
    return count


def problem_count() -> int:
    with connect() as conn:
        return conn.execute("SELECT COUNT(*) FROM problems").fetchone()[0]


def recommend_problems(
    discord_id: int,
    *,
    target_rating: int | None = None,
    min_offset: int = 100,
    max_offset: int = 200,
) -> sqlite3.Row | None:
    user = get_verified_user(discord_id)
    if not user:
        return None

    if target_rating is not None:
        low = high = target_rating
    else:
        rating = user["rating"] or 800
        low = max(800, rating - min_offset)
        high = rating + max_offset

    with connect() as conn:
        return conn.execute(
            """
            SELECT p.contest_id, p.problem_index, p.name, p.rating, p.tags
            FROM problems p
            WHERE p.rating BETWEEN ? AND ?
              AND NOT EXISTS (
                  SELECT 1
                  FROM solved_problems s
                  WHERE s.discord_id = ?
                    AND s.contest_id = p.contest_id
                    AND s.problem_index = p.problem_index
              )
            ORDER BY RANDOM()
            LIMIT 1
            """,
            (low, high, discord_id),
        ).fetchone()

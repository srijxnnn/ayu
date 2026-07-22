import sqlite3

from db.connection import connect, now


def upsert_verified_user(
    discord_id: int,
    cf_handle: str,
    rating: int | None,
    rank: str,
    max_rating: int | None,
) -> None:
    timestamp = now()
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO verified_users (
                discord_id, cf_handle, rating, rank, max_rating, verified_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(discord_id) DO UPDATE SET
                cf_handle = excluded.cf_handle,
                rating = excluded.rating,
                rank = excluded.rank,
                max_rating = excluded.max_rating,
                updated_at = excluded.updated_at
            """,
            (discord_id, cf_handle, rating, rank, max_rating, timestamp, timestamp),
        )


def get_verified_user(discord_id: int) -> sqlite3.Row | None:
    with connect() as conn:
        return conn.execute(
            "SELECT * FROM verified_users WHERE discord_id = ?",
            (discord_id,),
        ).fetchone()

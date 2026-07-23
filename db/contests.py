import sqlite3

from db.connection import connect

_CONFIG_ID = 1


def get_contest_reminder_config() -> sqlite3.Row | None:
    with connect() as conn:
        return conn.execute(
            """
            SELECT channel_id, role_id, enabled
            FROM contest_reminder_config
            WHERE id = ?
            """,
            (_CONFIG_ID,),
        ).fetchone()


def upsert_contest_reminder_config(*, channel_id: int, role_id: int) -> None:
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO contest_reminder_config (id, channel_id, role_id, enabled)
            VALUES (?, ?, ?, 1)
            ON CONFLICT(id) DO UPDATE SET
                channel_id = excluded.channel_id,
                role_id = excluded.role_id,
                enabled = 1
            """,
            (_CONFIG_ID, channel_id, role_id),
        )


def disable_contest_reminder_config() -> bool:
    with connect() as conn:
        cur = conn.execute(
            """
            UPDATE contest_reminder_config
            SET enabled = 0
            WHERE id = ?
            """,
            (_CONFIG_ID,),
        )
        return cur.rowcount > 0


def already_reminded(contest_id: int) -> bool:
    with connect() as conn:
        row = conn.execute(
            """
            SELECT 1
            FROM contest_reminders_sent
            WHERE contest_id = ?
            """,
            (contest_id,),
        ).fetchone()
        return row is not None


def record_contest_reminder(contest_id: int) -> None:
    with connect() as conn:
        conn.execute(
            """
            INSERT OR IGNORE INTO contest_reminders_sent (contest_id)
            VALUES (?)
            """,
            (contest_id,),
        )

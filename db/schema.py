from db.connection import connect


def init_db() -> None:
    with connect() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS verified_users (
                discord_id INTEGER PRIMARY KEY,
                cf_handle TEXT NOT NULL UNIQUE,
                rating INTEGER,
                rank TEXT,
                max_rating INTEGER,
                verified_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS solved_problems (
                discord_id INTEGER NOT NULL,
                contest_id INTEGER NOT NULL,
                problem_index TEXT NOT NULL,
                PRIMARY KEY (discord_id, contest_id, problem_index),
                FOREIGN KEY (discord_id)
                    REFERENCES verified_users(discord_id)
                    ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS problems (
                contest_id INTEGER NOT NULL,
                problem_index TEXT NOT NULL,
                name TEXT NOT NULL,
                rating INTEGER,
                tags TEXT NOT NULL DEFAULT '[]',
                PRIMARY KEY (contest_id, problem_index)
            );
            """
        )

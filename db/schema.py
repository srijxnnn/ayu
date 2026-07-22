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

            CREATE TABLE IF NOT EXISTS daily_problem_config (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                channel_id INTEGER NOT NULL,
                hour INTEGER NOT NULL,
                minute INTEGER NOT NULL,
                timezone TEXT NOT NULL DEFAULT 'Asia/Kolkata',
                min_rating INTEGER NOT NULL DEFAULT 1000,
                max_rating INTEGER NOT NULL DEFAULT 1400,
                enabled INTEGER NOT NULL DEFAULT 1
            );

            CREATE TABLE IF NOT EXISTS daily_problems_posted (
                posted_date TEXT PRIMARY KEY,
                contest_id INTEGER NOT NULL,
                problem_index TEXT NOT NULL
            );
            """
        )

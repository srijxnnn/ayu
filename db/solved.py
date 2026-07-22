from db.connection import connect


def replace_solved_problems(
    discord_id: int,
    problems: list[tuple[int, str]],
) -> int:
    with connect() as conn:
        conn.execute(
            "DELETE FROM solved_problems WHERE discord_id = ?",
            (discord_id,),
        )
        conn.executemany(
            """
            INSERT OR IGNORE INTO solved_problems (discord_id, contest_id, problem_index)
            VALUES (?, ?, ?)
            """,
            [(discord_id, contest_id, index) for contest_id, index in problems],
        )
        count = conn.execute(
            "SELECT COUNT(*) FROM solved_problems WHERE discord_id = ?",
            (discord_id,),
        ).fetchone()[0]
    return count


def get_solved_keys(discord_id: int) -> set[tuple[int, str]]:
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT contest_id, problem_index
            FROM solved_problems
            WHERE discord_id = ?
            """,
            (discord_id,),
        ).fetchall()
    return {(row["contest_id"], row["problem_index"]) for row in rows}

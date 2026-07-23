import db
from codeforces import get_solved_problems


async def save_user_data(
    discord_id: int,
    cf_handle: str,
    user: dict,
    *,
    sync_solved: bool = True,
) -> tuple[str, int | None, int]:
    rank = (user.get("rank") or "unrated").lower()
    rating = user.get("rating")

    db.upsert_verified_user(
        discord_id=discord_id,
        cf_handle=cf_handle,
        rating=rating,
        rank=rank,
        max_rating=user.get("maxRating"),
    )

    solved_count = 0
    if sync_solved:
        solved = await get_solved_problems(cf_handle)
        solved_count = db.replace_solved_problems(discord_id, solved)

    return rank, rating, solved_count


async def has_solved_problem(
    discord_id: int,
    cf_handle: str,
    contest_id: int,
    problem_index: str,
) -> bool:
    if (contest_id, problem_index) in db.get_solved_keys(discord_id):
        return True

    solved = await get_solved_problems(cf_handle)
    return (contest_id, problem_index) in solved

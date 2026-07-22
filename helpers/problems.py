import db
from codeforces import get_problemset


async def ensure_problem_cache() -> bool:
    if db.problem_count() > 0:
        return True

    problems = await get_problemset()
    if not problems:
        return False

    db.upsert_problems(problems)
    return True

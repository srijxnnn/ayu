from datetime import UTC, datetime

from codeforces.client import get_json


async def get_user(handle: str) -> dict | None:
    data = await get_json("user.info", {"handles": handle})
    if not data or not data.get("result"):
        return None

    return data["result"][0]


async def get_solved_problems(handle: str) -> list[tuple[int, str]]:
    data = await get_json("user.status", {"handle": handle})
    if not data or not data.get("result"):
        return []

    solved: set[tuple[int, str]] = set()
    for submission in data["result"]:
        if submission.get("verdict") != "OK":
            continue

        problem = submission["problem"]
        contest_id = problem.get("contestId")
        index = problem.get("index")
        if contest_id is None or index is None:
            continue

        solved.add((contest_id, index))

    return sorted(solved)


async def get_solved_with_dates(
    handle: str,
) -> list[tuple[datetime, int, str]]:
    data = await get_json("user.status", {"handle": handle})
    if not data or not data.get("result"):
        return []

    first_solved: dict[tuple[int, str], datetime] = {}
    for submission in data["result"]:
        if submission.get("verdict") != "OK":
            continue

        problem = submission["problem"]
        contest_id = problem.get("contestId")
        index = problem.get("index")
        if contest_id is None or index is None:
            continue

        solved_at = datetime.fromtimestamp(
            submission["creationTimeSeconds"],
            tz=UTC,
        )
        key = (contest_id, index)
        if key not in first_solved or solved_at < first_solved[key]:
            first_solved[key] = solved_at

    return sorted(
        (solved_at, contest_id, index)
        for (contest_id, index), solved_at in first_solved.items()
    )

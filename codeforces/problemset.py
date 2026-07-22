import json

from codeforces.client import get_json


async def get_problemset() -> list[tuple[int, str, str, int | None, str]]:
    data = await get_json("problemset.problems")
    if not data:
        return []

    rows: list[tuple[int, str, str, int | None, str]] = []

    for problem in data["result"]["problems"]:
        contest_id = problem.get("contestId")
        index = problem.get("index")
        name = problem.get("name")

        if contest_id is None or index is None or not name:
            continue

        rows.append(
            (
                contest_id,
                index,
                name,
                problem.get("rating"),
                json.dumps(problem.get("tags") or []),
            )
        )

    return rows

from codeforces.client import get_json


async def get_upcoming_contests() -> list[dict]:
    data = await get_json("contest.list")
    if not data:
        return []

    contests: list[dict] = []
    for contest in data["result"]:
        if contest.get("phase") != "BEFORE":
            continue
        if contest.get("startTimeSeconds") is None:
            continue
        contests.append(contest)

    return contests

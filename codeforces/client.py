import aiohttp

BASE_URL = "https://codeforces.com/api"


async def get_json(method: str, params: dict | None = None) -> dict | None:
    url = f"{BASE_URL}/{method}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as res:
            data = await res.json()

    if data.get("status") != "OK":
        return None

    return data

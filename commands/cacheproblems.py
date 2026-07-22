from discord.ext import commands

import db
from codeforces import get_problemset


class CacheProblems(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="cacheproblems")
    @commands.has_permissions(administrator=True)
    async def cache_problems(self, ctx: commands.Context):
        """download the codeforces problem database (admin only). usage: ;cacheproblems"""

        msg = await ctx.reply(
            "downloading problemset from codeforces...", mention_author=False
        )

        problems = await get_problemset()
        if not problems:
            await msg.edit(content="failed to fetch problemset.")
            return

        count = db.upsert_problems(problems)
        await msg.edit(content=f"cached **{count}** problems.")


async def setup(bot: commands.Bot):
    await bot.add_cog(CacheProblems(bot))

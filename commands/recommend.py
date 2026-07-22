from discord.ext import commands

import db
from codeforces import get_problemset


class Recommend(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="recommend")
    async def recommend(self, ctx: commands.Context):
        """suggest one unsolved problem near your rating. usage: ;recommend"""

        record = db.get_verified_user(ctx.author.id)
        if not record:
            await ctx.reply(f"run `{ctx.prefix}verify` first.", mention_author=False)
            return

        if db.problem_count() == 0:
            msg = await ctx.reply(
                "problem cache is empty - downloading problemset (one-time)...",
                mention_author=False,
            )
            problems = await get_problemset()
            if not problems:
                await msg.edit(content="failed to fetch problemset. try again later.")
                return
            db.upsert_problems(problems)
            await msg.delete()

        problem = db.recommend_problems(ctx.author.id)
        if not problem:
            await ctx.reply(
                f"no matching problems found. try `{ctx.prefix}sync` or ask an admin "
                f"to run `{ctx.prefix}cacheproblems`.",
                mention_author=False,
            )
            return

        problem_rating = problem["rating"] if problem["rating"] is not None else "?"
        url = (
            f"https://codeforces.com/problemset/problem/"
            f"{problem['contest_id']}/{problem['problem_index']}"
        )
        user_rating = record["rating"] or 800
        await ctx.reply(
            f"recommended for **{record['cf_handle']}** (rating {user_rating}):\n"
            f"[{problem['contest_id']}{problem['problem_index']}]({url}) "
            f"**{problem['name']}** ({problem_rating})",
            mention_author=False,
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Recommend(bot))

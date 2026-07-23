import discord
from discord.ext import commands

import db
from codeforces import get_solved_with_dates
from helpers.perf_chart import render_perf_chart
from helpers.problems import ensure_problem_cache


class Plot(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.group(name="plot", invoke_without_command=True)
    async def plot_group(self, ctx: commands.Context):
        """plot codeforces stats. usage: ;plot perf"""
        await ctx.reply(
            f"usage: `{ctx.prefix}plot perf` - solved problems over time",
            mention_author=False,
        )

    @plot_group.command(name="perf")
    async def perf(self, ctx: commands.Context):
        """chart solved problem ratings by date. usage: ;plot perf"""
        record = db.get_verified_user(ctx.author.id)
        if not record:
            await ctx.reply(f"run `{ctx.prefix}verify` first.", mention_author=False)
            return

        msg = await ctx.reply("fetching submissions...", mention_author=False)

        if not await ensure_problem_cache():
            await msg.edit(
                content=(
                    "problem cache is empty and could not be downloaded. "
                    f"ask an admin to run `{ctx.prefix}cacheproblems`."
                )
            )
            return

        solved = await get_solved_with_dates(record["cf_handle"])
        if not solved:
            await msg.edit(content="no accepted submissions found on codeforces.")
            return

        ratings = db.get_ratings_map()
        points = [
            (solved_at, ratings[(contest_id, index)])
            for solved_at, contest_id, index in solved
            if (contest_id, index) in ratings
            and ratings[(contest_id, index)] is not None
        ]
        if not points:
            await msg.edit(
                content=(
                    "no rated solved problems found. "
                    f"try `{ctx.prefix}sync` after caching problems."
                )
            )
            return

        chart = render_perf_chart(record["cf_handle"], record["rating"], points)
        file = discord.File(chart, filename="perf.png")
        await msg.delete()
        await ctx.send(
            f"**{record['cf_handle']}** - {len(points)} rated solves",
            file=file,
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Plot(bot))

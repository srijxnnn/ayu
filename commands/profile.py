from discord.ext import commands

import db
from helpers.daily import DEFAULT_TIMEZONE, effective_daily_streak


class Profile(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="profile")
    async def profile(self, ctx: commands.Context):
        """show your stored codeforces stats. usage: ;profile"""
        record = db.get_verified_user(ctx.author.id)
        if not record:
            await ctx.reply(f"run `{ctx.prefix}verify` first.", mention_author=False)
            return

        solved_count = len(db.get_solved_keys(ctx.author.id))
        rating = record["rating"] if record["rating"] is not None else "unrated"
        max_rating = (
            record["max_rating"] if record["max_rating"] is not None else "unrated"
        )

        config = db.get_daily_config()
        timezone = config["timezone"] if config else DEFAULT_TIMEZONE
        streak_row = db.get_daily_streak(ctx.author.id)
        streak = effective_daily_streak(
            streak_row["streak"] if streak_row else 0,
            streak_row["last_completed_date"] if streak_row else None,
            timezone,
        )

        await ctx.reply(
            f"**{record['cf_handle']}**\n"
            f"rank: **{record['rank'].title()}**\n"
            f"rating: **{rating}** (max **{max_rating}**)\n"
            f"solved (cached): **{solved_count}**\n"
            f"daily streak: **{streak}** day{'s' if streak != 1 else ''}",
            mention_author=False,
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Profile(bot))

from discord.ext import commands

import db


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

        await ctx.reply(
            f"**{record['cf_handle']}**\n"
            f"rank: **{record['rank'].title()}**\n"
            f"rating: **{rating}** (max **{max_rating}**)\n"
            f"solved (cached): **{solved_count}**",
            mention_author=False,
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Profile(bot))

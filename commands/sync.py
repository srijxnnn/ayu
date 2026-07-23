from discord.ext import commands

import db
from codeforces import get_user
from helpers import assign_rank_role, save_user_data


class Sync(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="sync")
    async def sync(self, ctx: commands.Context):
        """refresh rating, rank role, and solved problems. usage: ;sync"""
        record = db.get_verified_user(ctx.author.id)
        if not record:
            await ctx.reply(f"run `{ctx.prefix}verify` first.", mention_author=False)
            return

        user = await get_user(record["cf_handle"])
        if not user:
            await ctx.reply(
                "could not fetch your codeforces profile.", mention_author=False
            )
            return

        rank, rating, solved_count = await save_user_data(
            ctx.author.id,
            record["cf_handle"],
            user,
        )

        new_role = await assign_rank_role(ctx.author, rank)
        if not new_role:
            await ctx.reply(
                f"role for `{rank}` is not set up on this server.", mention_author=False
            )
            return

        rating_display = rating if rating is not None else "unrated"
        await ctx.reply(
            f"synced **{record['cf_handle']}** - **{rank}** ({rating_display}), "
            f"**{solved_count}** solved problems.",
            mention_author=False,
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Sync(bot))

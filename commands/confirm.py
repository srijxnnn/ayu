from discord.ext import commands

import state
from codeforces import get_user
from helpers import assign_rank_role, save_user_data


class Confirm(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="confirm")
    async def confirm(self, ctx: commands.Context):
        """confirm verification after setting the token on codeforces. usage: ;confirm"""

        data = state.pending.get(ctx.author.id)
        if not data:
            await ctx.reply(
                f"run `{ctx.prefix}verify <handle>` first.", mention_author=False
            )
            return

        user = await get_user(data["handle"])
        if not user:
            await ctx.reply("codeforces handle not found.", mention_author=False)
            return

        first_name = (user.get("firstName") or "").strip()
        last_name = (user.get("lastName") or "").strip()
        if not (data["token"] in first_name or data["token"] in last_name):
            await ctx.reply(
                "token not found in your codeforces **first name** or **last name** field. "
                "double-check settings and try again.",
                mention_author=False,
            )
            return

        rank, rating, solved_count = await save_user_data(
            ctx.author.id,
            data["handle"],
            user,
        )

        new_role = await assign_rank_role(ctx.author, rank)
        if not new_role:
            await ctx.reply(
                f"role for `{rank}` is not set up on this server.", mention_author=False
            )
            return

        del state.pending[ctx.author.id]

        rating_display = rating if rating is not None else "unrated"
        await ctx.reply(
            f"verified **{data['handle']}** - **{rank.title()}** ({rating_display}). "
            f"synced **{solved_count}** solved problems.\n"
            f"run `{ctx.prefix}gimme` to get problem suggestions.",
            mention_author=False,
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Confirm(bot))

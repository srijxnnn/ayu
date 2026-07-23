import secrets

import discord
from discord.ext import commands

import state


class Verify(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="verify")
    async def verify(self, ctx: commands.Context, handle: str):
        """start codeforces verification. usage: ;verify your_handle"""

        token = f"AYU-{secrets.token_hex(4)}"
        state.pending[ctx.author.id] = {"handle": handle, "token": token}

        instructions = (
            f"**codeforces verification for `{handle}`**\n\n"
            f"1. go to https://codeforces.com/settings/social\n"
            f"2. set **first name** or **last name** to: `{token}`\n"
            f"3. save, then run `{ctx.prefix}confirm` in the server."
        )

        try:
            await ctx.author.send(instructions, suppress_embeds=True)
            await ctx.reply(
                "check your dms for verification instructions.", mention_author=False
            )
        except discord.Forbidden:
            await ctx.reply(instructions, mention_author=False)


async def setup(bot: commands.Bot):
    await bot.add_cog(Verify(bot))

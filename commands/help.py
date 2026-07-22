from discord.ext import commands


class Help(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="help")
    async def help_command(self, ctx: commands.Context, *, command: str | None = None):
        """list commands or show help for one command. usage: ;help [command]"""
        prefix = ctx.prefix

        if command:
            cmd = self.bot.get_command(command.lower())
            if not cmd:
                await ctx.reply(
                    f"unknown command `{command}`. run `{prefix}help` for a list.",
                    mention_author=False,
                )
                return

            signature = f" {cmd.signature}" if cmd.signature else ""
            description = cmd.help or "no description."
            await ctx.reply(
                f"**{cmd.name}**{signature}\n{description}",
                mention_author=False,
            )
            return

        lines = [
            "**commands**\n",
            f"`{prefix}verify <handle>` - start codeforces verification",
            f"`{prefix}confirm` - finish verification after setting token on CF",
            f"`{prefix}sync` - refresh rating, rank role, and solved problems",
            f"`{prefix}profile` - show your stored codeforces stats",
            f"`{prefix}recommend` - get a random unsolved problem near your rating",
            f"`{prefix}help [command]` - show this list or help for one command",
            f"`{prefix}cacheproblems` - cache CF problemset (admin only)",
        ]
        await ctx.reply("\n".join(lines), mention_author=False)


async def setup(bot: commands.Bot):
    await bot.add_cog(Help(bot))

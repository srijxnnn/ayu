import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

import db
from commands import EXTENSIONS

load_dotenv()

PREFIX = os.getenv("PREFIX", ";")
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True


class AyuContext(commands.Context):
    async def send(self, *args, **kwargs):
        kwargs.setdefault("suppress_embeds", True)
        return await super().send(*args, **kwargs)

    async def reply(self, *args, **kwargs):
        kwargs.setdefault("suppress_embeds", True)
        return await super().reply(*args, **kwargs)


class AyuBot(commands.Bot):
    async def get_context(self, message, *, cls=AyuContext):
        return await super().get_context(message, cls=cls)


bot = AyuBot(command_prefix=PREFIX, intents=intents, help_command=None)


@bot.event
async def on_command_error(ctx: commands.Context, error: commands.CommandError):
    if isinstance(error, commands.CommandNotFound):
        return

    if isinstance(error, commands.MissingRequiredArgument):
        cmd = ctx.command
        signature = f"{cmd.name} {cmd.signature}" if cmd else "?"
        await ctx.reply(
            f"missing `{error.param.name}`. usage: `{ctx.prefix}{signature}`",
            mention_author=False,
        )
        return

    if isinstance(error, commands.BadArgument):
        cmd = ctx.command
        signature = f"{cmd.name} {cmd.signature}" if cmd else "?"
        await ctx.reply(
            f"invalid argument. usage: `{ctx.prefix}{signature}`",
            mention_author=False,
        )
        return

    if isinstance(error, commands.MissingPermissions):
        await ctx.reply(
            "you don't have permission to run this command.",
            mention_author=False,
        )
        return

    raise error


@bot.event
async def setup_hook():
    for extension in EXTENSIONS:
        await bot.load_extension(extension)


@bot.event
async def on_ready():
    db.init_db()
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.playing,
            name=f"run {PREFIX}help to get started",
        )
    )
    print(f"Logged in as {bot.user} (prefix: {PREFIX})")


if __name__ == "__main__":
    if not TOKEN:
        raise SystemExit("DISCORD_BOT_TOKEN is missing from .env")
    bot.run(TOKEN)

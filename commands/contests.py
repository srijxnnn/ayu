import discord
from discord.ext import commands, tasks

import db
from codeforces.contests import get_upcoming_contests
from helpers.contests import (
    contest_reminder_message,
    format_upcoming_contests,
    is_reminder_due,
    role_ping_mentions,
)


class Contests(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_load(self):
        self.contest_reminder_task.start()

    async def cog_unload(self):
        self.contest_reminder_task.cancel()

    @tasks.loop(minutes=1)
    async def contest_reminder_task(self):
        config = db.get_contest_reminder_config()
        if not config or not config["enabled"]:
            return

        channel = self.bot.get_channel(config["channel_id"])
        if channel is None:
            return

        guild = channel.guild
        role = guild.get_role(config["role_id"])
        if role is None:
            return

        contests = await get_upcoming_contests()
        for contest in contests:
            contest_id = contest["id"]
            start_time = contest["startTimeSeconds"]

            if not is_reminder_due(start_time):
                continue
            if db.already_reminded(contest_id):
                continue

            await channel.send(
                contest_reminder_message(contest, role.mention),
                allowed_mentions=role_ping_mentions(role),
            )
            db.record_contest_reminder(contest_id)

    @contest_reminder_task.before_loop
    async def before_contest_reminder_task(self):
        await self.bot.wait_until_ready()

    @commands.group(name="contest", invoke_without_command=True)
    async def contest(self, ctx: commands.Context):
        """configure contest reminders. usage: ;contest set/status/stop/test/upcoming"""
        await ctx.reply(
            f"usage: `{ctx.prefix}contest set #channel @role` - "
            f"see `{ctx.prefix}help contest` for more.",
            mention_author=False,
        )

    @contest.command(name="set")
    @commands.has_permissions(administrator=True)
    async def contest_set(
        self,
        ctx: commands.Context,
        channel: discord.TextChannel,
        role: discord.Role,
    ):
        """set the reminder channel and role to ping (admin only).
        usage: ;contest set #channel @role"""

        db.upsert_contest_reminder_config(
            channel_id=channel.id,
            role_id=role.id,
        )

        await ctx.reply(
            f"contest reminders enabled in {channel.mention}, "
            f"pinging {role.mention} 1 hour before each contest.",
            mention_author=False,
        )

    @contest.command(name="stop")
    @commands.has_permissions(administrator=True)
    async def contest_stop(self, ctx: commands.Context):
        """disable contest reminders (admin only). usage: ;contest stop"""

        if db.disable_contest_reminder_config():
            await ctx.reply("contest reminders disabled.", mention_author=False)
        else:
            await ctx.reply("no contest reminder config found.", mention_author=False)

    @contest.command(name="test")
    @commands.has_permissions(administrator=True)
    async def contest_test(self, ctx: commands.Context):
        """send a test reminder with the configured role ping (admin only).
        usage: ;contest test"""

        config = db.get_contest_reminder_config()
        if not config or not config["enabled"]:
            await ctx.reply(
                f"run `{ctx.prefix}contest set #channel @role` first.",
                mention_author=False,
            )
            return

        channel = self.bot.get_channel(config["channel_id"])
        if channel is None:
            await ctx.reply(
                "configured channel not found. run `;contest set` again.",
                mention_author=False,
            )
            return

        role = ctx.guild.get_role(config["role_id"]) if ctx.guild else None
        if role is None:
            await ctx.reply(
                "configured role not found. run `;contest set` again.",
                mention_author=False,
            )
            return

        await channel.send(
            "**contest reminder (test)**\n\n"
            "this is a test ping — real reminders go out 1 hour before each contest.\n\n"
            f"{role.mention}",
            allowed_mentions=role_ping_mentions(role),
        )
        await ctx.reply(
            f"sent test reminder to {channel.mention}.",
            mention_author=False,
        )

    @contest.command(name="upcoming")
    async def contest_upcoming(self, ctx: commands.Context, count: int = 5):
        """list upcoming codeforces contests. usage: ;contest upcoming [count]"""

        if count < 1 or count > 10:
            await ctx.reply(
                "count must be between 1 and 10.",
                mention_author=False,
            )
            return

        contests = await get_upcoming_contests()
        if not contests:
            await ctx.reply(
                "could not fetch contests or none are scheduled.",
                mention_author=False,
            )
            return

        await ctx.reply(
            format_upcoming_contests(contests, limit=count),
            mention_author=False,
        )

    @contest.command(name="status")
    async def contest_status(self, ctx: commands.Context):
        """show the current contest reminder config. usage: ;contest status"""

        config = db.get_contest_reminder_config()
        if not config or not config["enabled"]:
            await ctx.reply(
                f"contest reminders are off. admins can run "
                f"`{ctx.prefix}contest set #channel @role`.",
                mention_author=False,
            )
            return

        channel = self.bot.get_channel(config["channel_id"])
        channel_label = channel.mention if channel else f"`{config['channel_id']}`"

        role = ctx.guild.get_role(config["role_id"]) if ctx.guild else None
        role_label = role.mention if role else f"`{config['role_id']}`"

        await ctx.reply(
            f"contest reminders in {channel_label}, pinging {role_label} "
            f"1 hour before each contest.",
            mention_author=False,
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Contests(bot))

import discord
from discord.ext import commands, tasks

import db
from helpers.daily import (
    DEFAULT_MAX_RATING,
    DEFAULT_MIN_RATING,
    DEFAULT_TIMEZONE,
    daily_problem_message,
    format_rating_phrase,
    format_rating_value,
    is_scheduled_now,
    parse_time,
    problem_url,
    today_iso,
    validate_rating_range,
    validate_timezone,
)
from helpers.problems import ensure_problem_cache
from helpers.users import has_solved_problem


class Daily(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_load(self):
        self.daily_problem_task.start()

    async def cog_unload(self):
        self.daily_problem_task.cancel()

    @tasks.loop(minutes=1)
    async def daily_problem_task(self):
        config = db.get_daily_config()
        if config and config["enabled"] and is_scheduled_now(config):
            await self._post_daily_problem(config)

    @daily_problem_task.before_loop
    async def before_daily_problem_task(self):
        await self.bot.wait_until_ready()

    async def _post_daily_problem(self, config) -> bool:
        today = today_iso(config["timezone"])

        if db.already_posted_today(today):
            return False

        if not await ensure_problem_cache():
            return False

        problem = db.pick_daily_problem(
            min_rating=config["min_rating"],
            max_rating=config["max_rating"],
        )
        if not problem:
            return False

        channel = self.bot.get_channel(config["channel_id"])
        if channel is None:
            return False

        await channel.send(daily_problem_message(problem))
        db.record_daily_post(today, problem["contest_id"], problem["problem_index"])
        return True

    @commands.group(name="daily", invoke_without_command=True)
    async def daily(self, ctx: commands.Context):
        """configure automatic daily practice problems. usage: ;daily set/status/done/stop/now"""
        await ctx.reply(
            f"usage: `{ctx.prefix}daily set #channel HH:MM [min] [max]` - "
            f"see `{ctx.prefix}help daily` for more.",
            mention_author=False,
        )

    @daily.command(name="set")
    @commands.has_permissions(administrator=True)
    async def daily_set(
        self,
        ctx: commands.Context,
        channel: discord.TextChannel,
        time: str,
        min_rating: int | None = None,
        max_rating: int | None = None,
    ):
        """set the daily problem channel and posting time (admin only).
        usage: ;daily set #channel HH:MM [min] [max]"""

        parsed = parse_time(time)
        if parsed is None:
            await ctx.reply(
                "time must be in 24h format, e.g. `09:00` or `18:30`.",
                mention_author=False,
            )
            return

        hour, minute = parsed

        if min_rating is None and max_rating is None:
            min_rating, max_rating = DEFAULT_MIN_RATING, DEFAULT_MAX_RATING
        elif min_rating is None or max_rating is None:
            await ctx.reply(
                "provide both min and max rating, e.g. `1000 1400`.",
                mention_author=False,
            )
            return
        elif error := validate_rating_range(min_rating, max_rating):
            await ctx.reply(error, mention_author=False)
            return

        existing = db.get_daily_config()
        timezone = existing["timezone"] if existing else DEFAULT_TIMEZONE

        db.upsert_daily_config(
            channel_id=channel.id,
            hour=hour,
            minute=minute,
            timezone=timezone,
            min_rating=min_rating,
            max_rating=max_rating,
        )

        await ctx.reply(
            f"daily problem scheduled in {channel.mention} at "
            f"**{hour:02d}:{minute:02d}** ({timezone}), "
            f"{format_rating_phrase(min_rating, max_rating)}.",
            mention_author=False,
        )

    @daily.command(name="timezone")
    @commands.has_permissions(administrator=True)
    async def daily_timezone(self, ctx: commands.Context, timezone: str):
        """set the timezone for daily posts (admin only).
        usage: ;daily timezone Asia/Kolkata"""

        if error := validate_timezone(timezone):
            await ctx.reply(error, mention_author=False)
            return

        if not db.update_daily_timezone(timezone):
            await ctx.reply(
                f"run `{ctx.prefix}daily set #channel HH:MM` first.",
                mention_author=False,
            )
            return

        await ctx.reply(
            f"daily problem timezone set to **{timezone}**.",
            mention_author=False,
        )

    @daily.command(name="stop")
    @commands.has_permissions(administrator=True)
    async def daily_stop(self, ctx: commands.Context):
        """disable daily problem posts (admin only). usage: ;daily stop"""

        if db.disable_daily_config():
            await ctx.reply("daily problem posts disabled.", mention_author=False)
        else:
            await ctx.reply(
                "no daily problem schedule is configured.", mention_author=False
            )

    @daily.command(name="done")
    async def daily_done(self, ctx: commands.Context):
        """mark today's daily problem as solved and update your streak.
        usage: ;daily done"""

        record = db.get_verified_user(ctx.author.id)
        if not record:
            await ctx.reply(f"run `{ctx.prefix}verify` first.", mention_author=False)
            return

        config = db.get_daily_config()
        timezone = config["timezone"] if config else DEFAULT_TIMEZONE
        today = today_iso(timezone)

        posted = db.get_posted_daily_problem(today)
        if not posted:
            await ctx.reply(
                "no daily problem has been posted today yet.",
                mention_author=False,
            )
            return

        contest_id = posted["contest_id"]
        problem_index = posted["problem_index"]

        if not await has_solved_problem(
            ctx.author.id,
            record["cf_handle"],
            contest_id,
            problem_index,
        ):
            await ctx.reply(
                f"you haven't solved today's daily problem "
                f"**{contest_id}{problem_index}** yet.",
                mention_author=False,
            )
            return

        streak, already_done = db.record_daily_completion(ctx.author.id, today)
        if already_done:
            await ctx.reply(
                f"you already marked today's daily as done. "
                f"streak: **{streak}** day{'s' if streak != 1 else ''}.",
                mention_author=False,
            )
            return

        await ctx.reply(
            f"daily complete! streak: **{streak}** day{'s' if streak != 1 else ''}.",
            mention_author=False,
        )

    @daily.command(name="status")
    async def daily_status(self, ctx: commands.Context):
        """show the current daily problem schedule. usage: ;daily status"""

        config = db.get_daily_config()
        if not config or not config["enabled"]:
            await ctx.reply(
                f"no active daily schedule. admins can run "
                f"`{ctx.prefix}daily set #channel HH:MM`.",
                mention_author=False,
            )
            return

        channel = self.bot.get_channel(config["channel_id"])
        channel_label = channel.mention if channel else f"`{config['channel_id']}`"

        await ctx.reply(
            f"daily problem in {channel_label} at "
            f"**{config['hour']:02d}:{config['minute']:02d}** "
            f"({config['timezone']}), ratings "
            f"{format_rating_value(config['min_rating'], config['max_rating'])}.",
            mention_author=False,
        )

    @daily.command(name="now")
    @commands.has_permissions(administrator=True)
    async def daily_now(self, ctx: commands.Context):
        """post today's daily problem immediately (admin only). usage: ;daily now"""

        config = db.get_daily_config()
        if not config or not config["enabled"]:
            await ctx.reply(
                f"run `{ctx.prefix}daily set #channel HH:MM` first.",
                mention_author=False,
            )
            return

        if not await ensure_problem_cache():
            await ctx.reply(
                "problem cache is empty and download failed. try again later.",
                mention_author=False,
            )
            return

        posted = await self._post_daily_problem(config)
        if posted:
            await ctx.reply("posted today's daily problem.", mention_author=False)
        else:
            await ctx.reply(
                "could not post - already posted today, no matching problems, "
                "or channel is missing.",
                mention_author=False,
            )


async def setup(bot: commands.Bot):
    await bot.add_cog(Daily(bot))

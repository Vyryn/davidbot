import asyncio
import json
import random
import discord

from discord import NotFound
from discord.ext import commands
from functions import (
    deltime,
    poll_ids,
    now,
    log,
    number_reactions,
    reactions_to_nums,
    bot_id,
    owner_id,
)


async def remind_routine(increments, user, author, message):
    if user is author:
        message = ":alarm_clock: **Reminder:** \n" + message
    else:
        message = f":alarm_clock: **Reminder from {author}**: \n" + message
    await asyncio.sleep(increments)
    await user.send(message)
    print(f"{user} has been sent their reminder {message}")


class Schedule(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Events
    # When bot is ready, print to console
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Cog {self.qualified_name} is ready.")


def setup(bot):
    bot.add_cog(Schedule(bot))

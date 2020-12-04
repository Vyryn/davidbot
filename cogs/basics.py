import asyncio
import json
import random
import discord

from discord import NotFound
from discord.ext import commands
from functions import deltime, poll_ids, now, log, number_reactions, reactions_to_nums, \
    bot_id, owner_id


async def remind_routine(increments, user, author, message):
    if user is author:
        message = ':alarm_clock: **Reminder:** \n' + message
    else:
        message = f':alarm_clock: **Reminder from {author}**: \n' + message
    await asyncio.sleep(increments)
    await user.send(message)
    print(f'{user} has been sent their reminder {message}')


class Basics(commands.Cog):

    def __init__(self, bot):
        # Save the auth and polls variables to file every 5 minutes
        # self.bg_task = self.bot.loop.create_task((300, reminder))
        self.bot = bot

    # Events
    # When bot is ready, print to console
    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Cog {self.qualified_name} is ready.')

    # =============================Message handler=========================
    @commands.Cog.listener()
    async def on_message(self, message):
        # ===========================LOG=============================
        ln = '\n'
        n_ln = '\\n'
        # Build a log of this message
        log_msg = ''
        log_dict = {'log': 'message', 'timestamp': now()}
        if message.author.bot:
            log_msg += f'Message logged at {now()} by Bot {message.author}'
            log_dict['bot'] = True
        else:
            log_msg += f'Message logged at {now()} by User {message.author}'
            log_dict['bot'] = False
        log_dict['author'] = {'id': message.author.id, 'name': message.author.name}
        if message.guild is not None:
            log_msg += f' in Guild: {message.guild} in Channel {message.channel}:'
            log_dict['guild'] = {'id': message.guild.id, 'name': message.guild.name}
            log_dict['channel'] = {'id': message.channel.id, 'name': message.channel.name}
        else:
            log_msg += f' in Channel {message.channel}:'
            log_dict['guild'] = {'id': 'private', 'name': message.author.name}
            log_dict['channel'] = {'id': message.channel.id, 'name': message.author.name}
        if message.content != "":
            log_msg += f" with Content: {message.system_content.replace(ln, n_ln)}"
            log_dict['content'] = message.content
        if len(message.embeds) > 0:
            log_msg += f' with Embed: {message.embeds[0].to_dict()}'
            log_dict['embed'] = message.embeds[0].to_dict()
        if len(message.attachments) > 0:
            log_msg += f' with Attachment: {message.attachments[0].filename},{message.attachments[0].url}'
            log_dict['attachment'] = {'filename': message.attachments[0].filename, 'url': message.attachments[0].url}
        # Log message
        # log(log_dict)
        try:
            log(log_msg, message)
        except AttributeError:
            print(log_msg)

    # Commands
    @commands.command(name='ping', aliases=['plonk'], description='Pong!')
    async def ping(self, ctx):
        """Returns the ping to the bot"""
        ping = round(self.bot.latency * 1000)
        await ctx.message.delete(delay=deltime)  # delete the command
        await ctx.send(f'Ping is {ping}ms.', delete_after=deltime)
        print(f'Ping command used by {ctx.author} at {now()} with ping {ping}')

    # Send you a reminder DM with a custom message in a custom amount of time
    @commands.command(name='remind', aliases=['rem', 're', 'r', 'remindme', 'tellme', 'timer'], pass_context=True,
                      description='Send reminders!')
    async def remind(self, ctx, *, reminder=None):
        """Reminds you what you tell it to.
                Example: remind Tell @neotheone he's a joker in 10m
                Your reminder needs to end with in and then the amount of time you want to be reminded in.
                New! Now you can also remind you're a joke in 10m @neotheone     to send him the reminder directly.
                Please note that abuse of reminding other people **will** result in your perms being edited so that you
                can't use the remind command at all.
                10s: 10 seconds from now
                10m: 10 minutes from now
                1h:   1 hour from now
                1d: tomorrow at this time
                1w: next week at this time
                1y: next year (or probably never, as the bot currently forgets reminders if it restarts)
        """
        try:
            print(ctx.message.raw_mentions[0])
            user = ctx.guild.get_member(ctx.message.raw_mentions[0])
        except IndexError:
            user = None
        if user is None:
            user = ctx.author
        t = reminder.rsplit(' in ', 1)
        reminder = t[0]
        increments = 0
        if t[1][:-1].isdecimal():  # true if in 15m format is proper, 1 letter at the end preceded by a number
            # preceded by in
            increments = int(t[1][:-1])  # number of increment to wait
            increment = t[1][-1]  # s, m, h, d, w, y
            time_options = {'s': 1, 'm': 60, 'h': 60 * 60, 'd': 60 * 60 * 24, 'w': 60 * 60 * 24 * 7,
                            'y': 60 * 60 * 24 * 365}
            increments *= time_options.get(increment, 1)
            print(f'{ctx.author} created a reminder to {user} for {increments} seconds from now; {t}')
            self.bg_task = self.bot.loop.create_task(remind_routine(increments, user, ctx.author, reminder))
            await ctx.send(f"Got it. I'll send the reminder in {increments} seconds.", delete_after=deltime)
        else:
            await ctx.send('Please enter a valid time interval. You can use s, m, h, d, w, y as your interval time '
                           'prefix.', delete_after=deltime)
        await ctx.message.delete(delay=deltime)  # delete the command
        print(f'Remind command used by {ctx.author} at {now()} with reminder {reminder} to user {user} for '
              f'time {increments}.')

    @commands.command(name='time', description='Check the current time')
    async def time(self, ctx):
        """Check the current time
        """
        await ctx.send(f'It is currently {now()}.')
        print(f'Time command used by {ctx.author} at {now()}.')

    @commands.command(description='See who contributed to the bot.')
    async def credits(self, ctx):
        await ctx.send("""Davidbot created by Vyryn#4618.
        Big thanks to the beta testers: Chippy_X#4905, Slimey2#9610, RotorBoy#7385, Revoxxer#0042 and DARTHEDDEUS#3907.
        The bot was of course all made possible by Weyland#1569.
        Funny byline quotes by Stonewayne#6498.
        And of course thank you to everyone who contributed suggestions for improving David.""")


def setup(bot):
    bot.add_cog(Basics(bot))

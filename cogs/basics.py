import asyncio
import json
import random
import discord

from discord import NotFound
from discord.ext import commands
from functions import deltime, poll_ids, now, log, number_reactions, reactions_to_nums, \
    bot_id, set_polls, owner_id


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
        set_polls()
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
        log(log_msg, message)
        # print(log_msg)

    # ==============================Reaction handler======================================
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        # print(f'New reaction {payload.emoji} on message {payload.message_id} in {payload.channel_id} by user {
        # payload.user_id}.')
        # ===============================Polls==================================
        if payload.user_id == bot_id:
            pass
        else:
            if payload.message_id in poll_ids.keys():
                for channel in self.bot.get_all_channels():
                    if channel.id is poll_ids[payload.message_id]["id"]:
                        user = await self.bot.fetch_user(payload.user_id)
                        try:
                            user_responses = poll_ids[payload.message_id][user.id]
                        except KeyError:
                            poll_ids[payload.message_id][user.id] = 0
                            user_responses = 0
                        if user_responses < poll_ids[payload.message_id]['max']:
                            print(f'New reaction on poll {payload.message_id} by {user}.')
                            poll_ids[payload.message_id][reactions_to_nums[payload.emoji.name] - 1] += [user.id]
                            try:
                                poll_ids[payload.message_id][user.id] += 1
                            except KeyError:
                                poll_ids[payload.message_id][user.id] = 1
                            print(poll_ids)
                            try:
                                msg = await channel.fetch_message(payload.message_id)
                                new_embed = discord.Embed(title='', description='',
                                                          color=user.color)
                                new_embed.set_author(icon_url=user.avatar_url,
                                                     name=poll_ids[payload.message_id]["title"])
                                for i in range(0, 9):
                                    if len(poll_ids[payload.message_id].get(i, [])) > 0:
                                        new_embed.add_field(name=f"Option {i + 1}:",
                                                            value=len(poll_ids[payload.message_id][i]))
                                await msg.edit(embed=new_embed)
                                return
                            except NotFound:
                                continue
                        else:
                            await self.bot.get_channel(payload.channel_id).send(f'{user}, you have already replied '
                                                                                f'the maximum number of times '
                                                                                f'to that poll. If you want to change '
                                                                                f'your responses, remove '
                                                                                f'your previous reaction(s) and try '
                                                                                f'again.',
                                                                                delete_after=deltime)
                            await (await self.bot.get_channel(payload.channel_id).fetch_message(
                                payload.message_id)).remove_reaction(payload.emoji,
                                                                     self.bot.get_guild(payload.guild_id).get_member(
                                                                         payload.user_id))
        # print(f'Reaction {payload.emoji.name} added to message {payload.message_id} by user {payload.user_id}.') #temporarily commented for discord.py issue

    # Reaction removal handler
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        # print(f'New reaction {payload.emoji} on message {payload.message_id} in {payload.channel_id} by user {
        # payload.user_id}.') Deal with polls
        if payload.message_id in poll_ids.keys():
            for channel in self.bot.get_all_channels():
                if channel.id is poll_ids[payload.message_id]["id"]:
                    user = await self.bot.fetch_user(payload.user_id)
                    poll_ids[payload.message_id][reactions_to_nums[payload.emoji.name] - 1].remove(user.id)
                    poll_ids[payload.message_id][user.id] -= 1
                    print(poll_ids)
                    try:
                        msg = await channel.fetch_message(payload.message_id)
                        new_embed = discord.Embed(title='', description='', color=user.color)
                        new_embed.set_author(icon_url=user.avatar_url, name=poll_ids[payload.message_id]["title"])
                        for i in range(0, 9):
                            if len(poll_ids[payload.message_id].get(i, [])) > 0:
                                new_embed.add_field(name=f"Option {i + 1}:", value=len(poll_ids[payload.message_id][i]))
                        if len(new_embed.fields) == 0:
                            new_embed.add_field(name="Poll Results:", value="No votes yet.")
                        await msg.edit(embed=new_embed)
                        return
                    except NotFound:
                        continue
        # print(f'Reaction {payload.emoji.name} removed from message {payload.message_id} by user {payload.user_id}.') #temporarily commented for discord.py issue

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
                Example: ,remind Tell @neotheone he's a joker in 10m
                Your reminder needs to end with in and then the amount of time you want to be reminded in.
                New! Now you can also ,remind you're a joke in 10m @neotheone     to send him the reminder directly.
                Please note that abuse of reminding other people **will** result in your perms being edited so that you
                can't use the ,remind command at all.
                10s: 10 seconds from now
                10m: 10 minutes from now
                1h:   1 hour from now
                1d: tomorrow at this time
                1w: next week at this time
                1y: next year (or probably never, as the bot currently forgets reminders if it restarts)"""
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

#    @remind.error
#    async def remind_error(self, ctx, error):
#        await ctx.send(f'{ctx.author}, the correct usage is **`/remind <reminder> in <0s>/<0m>/<0h>/<0d>/<0w>/<0y>`** '
#                       f'\n That "in" is important.',
#                       delete_after=deltime)
#        print(f"Silly {ctx.author} couldn\'t figure out how to use Remind. (lol)")

    @commands.command(name='poll', pass_context=True, description='Create a poll.')
    async def create_poll(self, ctx, num_options=2, max_options=1, *, text):
        """Creates a poll.
            num_options is how many options your poll has
            max_options is the maximum number someone can select
            text is what your poll is asking
        """
        if num_options < 1:
            num_options = 1
        elif num_options > 9:
            num_options = 9
        embed = discord.Embed(title=f'Poll Results', color=ctx.author.color)
        embed.set_author(icon_url=ctx.author.avatar_url, name=f'{text}')
        results = f'No Votes Yet.'
        embed.add_field(name='Poll Results:', value=results)
        poll_message = await ctx.send(content=None, embed=embed)
        print(f'Created a new poll from the message in channel {poll_message.channel.id} with id {poll_message.id}.')
        poll_ids[poll_message.id] = {'id': poll_message.channel.id}
        poll_ids[poll_message.id]['title'] = text
        poll_ids[poll_message.id]['max'] = max_options
        for i in range(0, num_options):
            await poll_message.add_reaction(number_reactions[i])
            poll_ids[poll_message.id][i] = []
            await asyncio.sleep(0.1)
        with open('polls.json', 'r') as f:
            polls = json.load(f)
        polls[poll_message.id] = poll_ids[poll_message.id]
        with open('polls.json', 'w') as f:
            json.dump(polls, f, indent=4)
        print(poll_message.embeds[0].fields[0].value)
        print(f'Poll command used by {ctx.author} at {now()} with poll {text}.')

    # Adds +1 and -1 reactions to your message
    @commands.command(name='yesno', pass_context=True, description='Adds yes and no to your message')
    async def yessno(self, ctx, *, message):
        await ctx.message.add_reaction('\U00010031')
        await ctx.message.add_reaction('\U00010032')
        print(f'Yesno command used by {ctx.author} at {now()} with message {message}.')
        return

    @commands.command(name='time', description='Check the current time')
    async def time(self, ctx):
        """Check the current time
        """
        await ctx.send(f'It is currently {now()}.')
        print(f'Time command used by {ctx.author} at {now()}.')


def setup(bot):
    bot.add_cog(Basics(bot))

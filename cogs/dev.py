import time

import discord
import json
import ast
from discord import File
from discord.ext import commands
from functions import auth, default_auth, set_commanders, get_commanders, perms_info, deltime, embed_footer, now, \
    set_ignored_channels


def insert_returns(body):
    # Originally bits copied from nitros12 for eval command, not written by Vyryn. Modified later on.

    # insert return stmt if the last expression is a expression statement
    if isinstance(body[-1], ast.Expr):
        body[-1] = ast.Return(body[-1].value)
        ast.fix_missing_locations(body[-1])

    # for if statements, we insert returns into the body and the orelse
    if isinstance(body[-1], ast.If):
        insert_returns(body[-1].body)
        insert_returns(body[-1].orelse)

    # for with blocks, again we insert returns into the body
    if isinstance(body[-1], ast.With):
        insert_returns(body[-1].body)


class Dev(commands.Cog):

    def __init__(self, bot):
        set_commanders()
        self.bot = bot

    # Events
    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Cog {self.qualified_name} is ready.')

    # Commands
    # Echo what you said
    @commands.command(name='echo', aliases=['repeat', 'say'], pass_context=True, description='Says what you tell it')
    @commands.check(auth(1))
    async def echo(self, ctx, *, message):
        """Have the bot repeat your message.
                Requires: Auth level 1
                Message: The message to repeat"""
        await ctx.message.delete()  # delete the command
        await ctx.send(message)
        print(f'Echo command used by {ctx.author} at {now()} with message {message}')

    # Have the bot send a dm to someone with your message
    @commands.command(name='sendmsg', aliases=['dm', 'tell', 'message'], pass_context=True,
                      description='DM an unsuspecting user')
    @commands.check(auth(2))
    async def send(self, ctx, user: discord.User, *, message=None):
        """Sends a DM to a user of your choice
                Requires: Auth level 2
                User: The user to message
                Message: The message to send"""
        message = message or 'Someone is pranking you bro.'
        await ctx.message.delete()  # delete the command
        await ctx.send('Message sent.', delete_after=deltime)
        await user.send(message)
        print(f'Send command used by {ctx.author} at {now()} to user {user} with message {message}')

    # Check someone's  auth level
    @commands.group(name='auth', aliases=['who', 'check', 'authorize'], description='Check the Auth Level of a user')
    @commands.check(auth(1))
    async def autho(self, ctx):
        """/auth check returns the auth level of a given user
                        Requires: Auth level 1
                        Member: The discord member to check the auth level of
                        You can use /auth set <user> <level> if you have auth level 7"""
        # await ctx.send('Use /auth check, /auth set or /auth all')
        print(f'Auth command used by {ctx.author} at {now()}')
        pass

    # Checks a user's auth level
    @autho.command(name='check')
    async def check(self, ctx, user: discord.User = None, detail=''):
        if not user:
            user = ctx.author
        auth_level = get_commanders().get(str(user.id), default_auth)
        embed = discord.Embed(title='', description='', color=user.color)
        embed.set_author(icon_url=user.avatar_url, name=f'{user} is '
                                                        f'authorized at level {auth_level}')
        if detail != '':
            perms = ''
            for perm in sorted(perms_info.keys(), reverse=True):
                if perm <= auth_level:
                    perms += str(perm) + ': ' + perms_info.get(perm) + '\n'
            embed.add_field(name='The Details:', value=perms)
        embed.set_footer(text=embed_footer(ctx.author))
        await ctx.send(content=None, embed=embed, delete_after=deltime * 5)
        await ctx.message.delete(delay=deltime)  # delete the command
        print(f'Auth check command used by {ctx.author} at {now()}, {user} is authorized at level {auth_level}.')

    # sets a user's auth level
    @commands.command(name='authset')
    @commands.check(auth(7))
    async def authset(self, ctx, level, user: discord.User):
        commanders = get_commanders()
        level = int(level)
        if commanders[str(ctx.author.id)] > level and commanders.get(user.id, 0) < commanders[str(ctx.author.id)]:
            with open('auths.json', 'r') as f:
                auths = json.load(f)
            print(f'Changing {user} auth level to {level}')
            auths[str(user.id)] = level
            with open('auths.json', 'w') as f:
                json.dump(auths, f, indent=4)
            set_commanders()  # update variable in memory after having written to disc new perms
            await ctx.send(f'Changed {user} auth level to {auths[str(user.id)]}', delete_after=deltime)
        elif commanders[str(ctx.author.id)] <= level:
            await ctx.send(f"I'm sorry, but you can't set someone's auth level higher than your own.")
        else:
            await ctx.send(f"I'm sorry, but you can't change the auth level of someone with an auth level equal to or "
                           f"higher than you.")
        print(f'Authset command used by {ctx.author} at {now()} to set {user}\'s auth level to {level}')

    # lists all bot commanders and their auth levels
    @autho.command(name='all')
    @commands.check(auth(4))
    async def set(self, ctx):
        commanders = get_commanders()
        embed = discord.Embed(title='', description='', color=ctx.author.color)
        embed.set_author(icon_url=ctx.author.avatar_url, name='Here you go:')
        message = ''
        for c in commanders:
            message += (str(await self.bot.fetch_user(c)) + ': ' + str(commanders[c]) + '\n')
        embed.add_field(name='Bot Commanders:', value=message)
        embed.set_footer(text=embed_footer(ctx.author))
        await ctx.send(content=None, embed=embed)
        print(f'Auth All command used by {ctx.author} at {now()}')

    # Unload a cog
    @commands.command(name='unload', pass_context=True, description='Unload a cog')
    @commands.check(auth(4))
    async def unload(self, ctx, extension):
        """Unload a cog
                Requires: Auth level 4
                Extension: The cog to unload"""
        self.bot.unload_extension(f'cogs.{extension}')
        print(f'Unloaded {extension}')
        await ctx.send(f'Unloaded {extension}.', delete_after=deltime)
        await ctx.message.delete(delay=deltime)  # delete the command
        print(f'Unload command used by {ctx.author} at {now()} on cog {extension}')

    # Reload a cog
    @commands.command(name='reload', description='Reload a cog')
    @commands.check(auth(3))
    async def reload(self, ctx, extension):
        """Reload a cog
                Requires: Auth level 4
                Extension: The cog to reload"""
        self.bot.unload_extension(f'cogs.{extension}')
        self.bot.load_extension(f'cogs.{extension}')
        print(f'Reloaded {extension}')
        await ctx.send(f'Reloaded {extension}', delete_after=deltime)
        await ctx.message.delete(delay=deltime)  # delete the command
        print(f'Reload command used by {ctx.author} at {now()} on cog {extension}')

    # Update bot status
    @commands.command(name='status', description='Change what the bot is playing')
    @commands.check(auth(5))
    async def status(self, ctx, *, message=''):
        """Change the bot's "playing" status
                Requires: Auth level 5
                Message: The message to change it to"""
        await self.bot.change_presence(activity=discord.Game(message))
        print(f'Updated status to {message}.')
        await ctx.send(f'Updated status to {message}.', delete_after=deltime)
        await ctx.message.delete(delay=deltime)  # delete the command
        print(f'Status command used by {ctx.author} at {now()} to set bot status to {message}')

    @commands.command(name='eval', description='Evaluates input.')
    @commands.check(auth(9))
    async def eval_fn(self, ctx, *, cmd):
        """Evaluates input.
        This command requires Auth 9 for obvious reasons.
        """
        starttime = time.time_ns()
        fn_name = "_eval_expr"

        cmd = cmd.strip("` ")
        if cmd[0:2] == 'py':  # Cut out py for ```py``` built in code blocks
            cmd = cmd[2:]
        # add a layer of indentation
        cmd = "\n".join(f"    {i}" for i in cmd.splitlines())

        # wrap in async def body
        body = f"async def {fn_name}():\n{cmd}"

        parsed = ast.parse(body)
        body = parsed.body[0].body

        insert_returns(body)

        env = {
            'bot': ctx.bot,
            'discord': discord,
            'commands': commands,
            'ctx': ctx,
            'self': self,
            '__import__': __import__
        }
        exec(compile(parsed, filename="<ast>", mode="exec"), env)

        result = (await eval(f"{fn_name}()", env))
        endtime = time.time_ns()
        await ctx.send(f'Command took {(endtime - starttime) / 1000000}ms to run.\nResult: {result}')

    @commands.command(name='delete', description='Delete a single message by ID')
    @commands.check(auth(6))
    async def delete(self, ctx, message_id: int):
        """
        Deletes a single message.
        Requires: Auth 6.
        Used for cleaning up bot mistakes.
        """
        await (await ctx.channel.fetch_message(message_id)).delete()
        await ctx.message.delete(delay=deltime)  # delete the command
        print(f'Deleted message {message_id} in channel {ctx.channel} for user {ctx.author} at {now()}')


def setup(bot):
    bot.add_cog(Dev(bot))

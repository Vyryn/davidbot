import json
from json import JSONDecodeError
import traceback
import discord
import os
import random
import sys
import asyncio
from discord.ext import commands
from itertools import cycle
from functions import statuses, auth, get_prefix, deltime, owner_id, get_ignored_channels, set_ignored_channels
from privatevars import TOKEN

bot = commands.Bot(command_prefix=get_prefix)

# Events
@bot.event
async def on_ready():
    # Pick a random current status on startup
    await bot.change_presence(status=discord.Status.online, activity=discord.Game(random.choice(statuses)))
    print('Bot is ready.')


# ================================= Error Handler =================================
@bot.event
async def on_command_error(ctx, error):
    if hasattr(ctx.command, 'on_error'):
        print('An error occurred, but was handled command-locally.')
        return
    if isinstance(error, commands.NoPrivateMessage):
        try:
            await ctx.send(f'The {ctx.command} command can not be used in private messages.', delete_after=deltime)
        except:
            pass
        return print(f'Error, NoPrivateMessage in command {ctx.command}: {error.args}')
    elif isinstance(error, commands.CommandNotFound):
        print(f'Error, {ctx.author} triggered CommandNotFound in command {ctx.command}: {error.args[0]}')
        return
    elif isinstance(error, commands.MissingRequiredArgument):
        try:
            await ctx.send("Incomplete command.", delete_after=deltime)
        except:
            pass
        return print(f'Error, MissingRequiredArgument in command {ctx.command}: {error.args[0]}')
    elif isinstance(error, commands.MissingPermissions):
        try:
            await ctx.send(f'{ctx.author}, {error}', delete_after=deltime)
        except:
            pass
        return print(f'{ctx.author} tried to use {ctx.command} without sufficient permissions.')
    elif isinstance(error, commands.CheckFailure):
        try:
            await ctx.send(f'{ctx.author}, you are not authorized to perform this command in this channel. If you '
                           f'think this is a mistake, try using the command in #self-registration or '
                           f'#bot-control-room.', delete_after=deltime)
        except:
            pass
        return print(f'{ctx.author} tried to use {ctx.command} without sufficient auth level.')
    elif isinstance(error, JSONDecodeError):
        try:
            await ctx.send(f'{ctx.author}, that api appears to be down at the moment.', delete_after=deltime)
        except:
            pass
        return print(f'{ctx.author} tried to use {ctx.command} but got a JSONDecodeError.')
    elif isinstance(error, asyncio.TimeoutError):
        try:
            await ctx.send(f"{ctx.author}, you took too long. Please re-run the command to continue"
                           f" when you're ready.", delete_after=deltime)
        except:
            pass
        return print(f'{ctx.author} tried to use {ctx.command} but got a JSONDecodeError.')
    else:
        # get data from exception
        etype = type(error)
        trace = error.__traceback__
        # 'traceback' is the stdlib module, `import traceback`.
        lines = traceback.format_exception(etype, error, trace)
        # format_exception returns a list with line breaks embedded in the lines, so let's just stitch the elements together
        traceback_text = '```py\n'
        traceback_text += ''.join(lines)
        traceback_text += '\n```'
        try:
            await ctx.send(
                f"Hmm, something went wrong with {ctx.command}. I have let the developer know, and they will take a look.")
            await bot.get_user(owner_id).send(
                f'Hey Vyryn, there was an error in the command {ctx.command}: {error}.\n It was used by {ctx.author} in {ctx.guild}, {ctx.channel}.')
            await bot.get_user(owner_id).send(traceback_text)
        except:
            print(f"I was unable to send the error log for debugging.")
        print(traceback_text)
        # print(f'Error triggered: {error} in command {ctx.command}, {traceback.print_tb(error.__traceback__)}')
        return

        #
        # # get data from exception
        # etype = type(error)
        # trace = error.__traceback__
        # # 'traceback' is the stdlib module, `import traceback`.
        # lines = traceback.format_exception(etype, error, trace)
        # try:
        #     await ctx.send(f"It looks like that didn't go as expected. I've sent some information to the developer to "
        #                    f"attempt to determine the issue.\n{etype}")
        # except:
        #     pass
        # finally:
        #     # format_exception returns a list with line breaks embedded in the lines, so let's just stitch the elements together
        #     traceback_text = '```py\n'
        #     traceback_text += ''.join(lines)
        #     traceback_text += '\n```'
        #     await bot.get_user(owner_id).send(traceback_text)
        #     print(traceback_text)
        #     # print(f'Error triggered: {error} in command {ctx.command}, {traceback.print_tb(error.__traceback__)}')
        # return


# Global checks
# Checks if a user has the requested authorization level or not, is a coroutine for async operation
@bot.check_once
def channel_check(ctx):
    async def channel_perm_check(*args):
        no_command_channels = get_ignored_channels()
        for channel in no_command_channels:
            if int(channel) == ctx.channel.id:
                return False
        return True

    return channel_perm_check()


# Commands
@bot.command(name='load', description='Load a cog')
@commands.check(auth(4))
async def load(ctx, extension):
    """The command to load a cog
            Requires: Auth level 4
            Extension: the cog to load"""
    bot.load_extension(f'cogs.{extension}')
    print(f'Loaded {extension}.')
    await ctx.send(f'Loaded {extension}.', delete_after=deltime)
    await ctx.message.delete(delay=deltime)  # delete the command


@bot.command(name='ignorech', description='Make the bot ignore commands in the channel this is used in.')
@commands.check(auth(4))
async def ignorech(ctx):
    ch_id = str(ctx.channel.id)
    no_command_channels = get_ignored_channels()
    no_command_channels.append(ch_id)
    with open('ignored_channels.json', 'w') as f:
        json.dump(no_command_channels, f, indent=4)
    set_ignored_channels()
    await ctx.send("Adding channel to ignore list.", delete_after=deltime)



@bot.command(name='restart', description='Restart the bot')
@commands.check(auth(5))
async def restart(ctx):
    """The command to restart the bot
        Requires: Auth level 5
        """
    await bot.change_presence(status=discord.Status.idle, activity=discord.Game("Restarting..."))
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            bot.unload_extension(f'cogs.{filename[:-3]}')  # unload each extension gracefully before restart
    os.execv(sys.executable, ['python'] + sys.argv)


# load all cogs in cogs folder at launch
for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')  # load up each extension

# run bot
bot.run(TOKEN)

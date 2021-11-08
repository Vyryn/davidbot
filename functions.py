import datetime
import json
from attr import dataclass

import discord

# The default global bot prefix
global_prefix = ';'
# The directory for cogs
cogs_dir = 'cogs'
# The id of the bot creator
owner_id = 125449182663278592
# The id of the bot
bot_id = 670443801474760734
# Default number of seconds to wait before deleting many bot responses and player commands
deltime = 10
# The bot commanders (imported from a file)
bot_commanders = {}  # {125449182663278592: 10, 631938498722529310: 7}
# The ids of ongoing polls (imported from a file)
poll_ids = {}
# Whether this person has used a command that requires a confirmation
confirmed_ids = {}

# Some channel and role IDs
ping_role = 680917298906923214
evocati_role = 493920914082234388
event_role = 728332957546446880
organizer_role = 525566800826466307
candidate_role = 540584857068372007
recruiter_role = 261396521805807617  # This is actually HR. Recruiter: 376500752203644928
visitor_role = 96472823354118144
corp_tag_id = 92031682596601856
corp_shield_tag_id = 315095427361800192
registration_channel = 204841604522049536
log_channel = 272278325244723200  # 666816919399170049 in testing server
div_req_notif_ch = 'recruitment'

# The default URL for RSI profiles
DEFAULT_RSI_URL = 'https://robertsspaceindustries.com'
profiles_url = 'https://robertsspaceindustries.com/citizens/'

# The URL for the divison information picture
div_pic = "https://cdn.discordapp.com/attachments/229700730611564545/707964562472697906/CORPDeptsDivs_revised_c.png"

# No command channels: A list of channels the bot will not respond to messages in.
no_command_channels = []

# Some common aliases for divs
div_alternative_names = {'space': 'space security', 'ground': 'ground security', 'repossession': 'repo',
                         'human': 'human resources', 'medical': 'csar', 'exploration': 'cartography',
                         'military': 'space security', 'bounty hunting': 'repo', 'bounty': 'repo',
                         'pr': 'media', 'streamer': 'media', 'recruitment': 'human resources',
                         'extractions': 'extraction'
                         }
# div-dept mapping
divs = {'prospecting': 'exploration', 'cartography': 'exploration', 'research': 'exploration',
        'contracts': 'business', 'finance': 'business', 'trade': 'business',
        'space security': 'security', 'ground security': 'security', 'repo': 'security',
        'development': 'resources', 'transport': 'resources', 'extraction': 'resources',
        'diplomacy': 'social', 'training': 'social', 'human resources': 'social',
        'csar': 'support', 'engineering': 'support',
        'media': 'public relations', 'e-sports': 'public relations'
        }

# Some registration messages
timeout_msg = 'You took too long to respond. You will need to start the command over again if you wish to continue' \
              ' your application.'
get_a_person = "Okay, let me wake up the team in the Office. Depending on timezones, we'll see who we can get..."
welcome_david_msg = "Welcome {author} to the Corporation! I'm David. Please join The Corporation on RSI. Once your" \
                    " application is accepted, **__please type__** \n```\nok```\nOr, if at any stage this seems" \
                    " too difficult, type `help` and I'll get a real person, it just may take longer. Note you will " \
                    "need to be accepted on RSI to complete this process."
understand_david_msg = "Great. Now I know you can understand me :smiley:\nCan you **__please post your RSI handle__**" \
                       " here? Or, if you're not sure how to that, type `how` or type `help` to get help from a person."
help_david_msg = '@Recruiter, {} has requested a personal touch for assistance with their application.'

# The number of seconds to wait to time out the registration process from inactivity
timeout = 1800

# The bot randomly selects one of these statuses at startup
statuses = ["The Elevator to success is currently out of order, you will have to take the stairs.",
            "Never underestimate your abilities, that is your Boss's job.",
            "The successful business person is the one who discovers what is wrong with their business before their "
            "competitors do.",
            "The light at the end of the tunnel has been turned off, due to budget cuts.",
            "I love deadlines. Especially the whooshing sound they make as they fly by.",
            "I don't understand people who say 'I don't know how to thank you'. Like they have never heard of money.",
            "Being powerful is like being popular, if you have to tell people you are... you aren't.",
            "If ever in doubt, just keep smiling. It makes people wonder what you are really up to.",
            "It is easier to move from failure to success, than from excuses to success.",
            "I cannot make it to this week's crisis... my schedule is already full.",
            "Accept that some days you are the pigeon, and some days you are the Statue.",
            "If your competitor's are going to hate you... make sure that they spell your name right.",
            "The six most expensive words in business are; 'We've always done it that way.'",
            "If you are grouchy, irritable or just plain mean... there will be a 10,000 aUEC charge for putting up "
            "with you.",
            "Sometimes the best business practice is to remind people that you can be an asshole too.",
            "Some people are like clouds, when they disappear it is a beautiful day.",
            "Never argue with an idiot, they will always bring you down to their level and beat you with experience.",
            "Every successful business began with a single step.",
            "Compete until the competition brag about how they know you.",
            "To win without risk, is to triumph without glory."]
# Which discord perms are consider basic/important
basicperms = ['administrator', 'manage_guild', 'ban_members', 'manage_roles', 'manage_messages']
# Which discord perms are consider significant/notable
sigperms = ['deafen_members', 'kick_members', 'manage_channels', 'manage_emojis',
            'manage_nicknames', 'manage_webhooks', 'mention_everyone', 'move_members', 'mute_members',
            'priority_speaker', 'view_audit_log']
# Authorization level of someone not in bot_commanders. Think carefully before changing this.
default_auth = 0
# Bot commanders levels
perms_info = {0: '(No other dev perms)', 1: 'Can use echo and auth check', 2: 'Can make bot send DMs',
              3: 'Can reload cogs', 4: 'Can load and unload cogs', 5: 'Can update bot status',
              6: 'Can see the list of all bot commanders', 7: 'Can set other people\'s auth levels',
              8: 'Trusted for dangerous dev commands', 9: 'Can use eval', 10: 'Created me'}
number_reactions = ["1\u20e3", "2\u20e3", "3\u20e3", "4\u20e3", "5\u20e3", "6\u20e3", "7\u20e3",
                    "8\u20e3", "9\u20e3"]
reactions_to_nums = {"1⃣": 1, "2⃣": 2, "3⃣": 3, "4⃣": 4, "5⃣": 5, "6⃣": 6, "7⃣": 7, "8⃣": 8, "9⃣": 9}


# Helper method for opening a json
def load_json_var(name):
    with open(f'{name}.json', 'r') as f:
        return json.load(f)


# Helper method for writing a json
def write_json_var(name, obj):
    with open(f'{name}.json', 'w') as f:
        json.dump(obj, f, indent=4)

1
# Update the memory bot_commanders dict by reading from file
def set_commanders():
    global bot_commanders
    bot_commanders = load_json_var('auths')
    bot_commanders["125449182663278592"] = 10
    return


def get_ignored_channels():
    global no_command_channels
    return no_command_channels


# Update the memory ignored_channels list by reading from file
def set_ignored_channels():
    global no_command_channels
    no_command_channels = load_json_var('ignored_channels')
    return


# Return the bot_commanders dict
def get_commanders():
    global bot_commanders
    return bot_commanders


# Return the apikeys dict
def get_apikeys():
    global apikeys
    return apikeys


# Update the memory apikeys dict by reading from file
def set_apikeys():
    global apikeys
    apikeys = load_json_var('apikeys')
    return


# Save bot_commanders to file
def save_commanders():
    global bot_commanders
    write_json_var('auths', bot_commanders)
    return


# Save apikeys to file
def save_aipkeys():
    global apikeys
    write_json_var('apikeys', apikeys)
    return


# Checks if a user has the requested authorization level or not, is a coroutine for async operation
def auth(level):
    async def user_auth_check(ctx, *args):
        for uid in bot_commanders.keys():
            if int(uid) == ctx.author.id and bot_commanders.get(uid, default_auth) >= level:
                return True
        print('User not found to be auth\'d')
        return False

    return user_auth_check


# Checks if a user has the requested authorization level or not, is a coroutine for async operation
def channel_check(ctx):
    async def channel_perm_check(*args):
        for channel in no_command_channels:
            if int(channel) == ctx.channel.id:
                return True
        return False

    return channel_perm_check()


# Returns the bot prefix for the guild the message is within, or the global default prefix
def get_prefix(bot, message):
    global no_command_channels
    with open('ignored_channels.json', 'r') as f:
        no_command_channels = json.load(f)
    # outside a guild
    if not message.guild:
        return global_prefix
    else:
        # Get guild custom prefixes from file
        with open('prefixes.json', 'r') as f:
            prefixes = json.load(f)
        return prefixes[str(message.guild.id)]


# Returns current timestamp in the desired format, in this case MM/DD/YYYY HH:MM:SS
def now():
    return datetime.datetime.now().strftime("%m/%d/%y %H:%M:%S")


# Returns current datestamp as YYYY-MM-DD
def today():
    return datetime.date.today().strftime("%Y-%m-%d")


# For saying the footnot was requested by someone
def embed_footer(author):
    return f'Requested by {str(author)} at {now()}.'


# Log a message.
def log(message, mm):
    print(message)
    guild = mm.guild.name
    channel = mm.channel.name
    # logmsg = 'MSG@{}:  {}:{}'.format(now(), message['guild']['name'],message['channel']['name'])
    try:
        with open(f'./logs/{guild}/{channel}_{today()}_log.log', 'a+') as f:
            try:
                f.write(str(message) + '\n')
            except UnicodeEncodeError:
                f.write(f'WRN@{now()}: A UnicodeEncodeError occurred trying to write a message log.\n')
    except:
        try:
            with open(f'./logs/{guild}_{today()}_log.log', 'a+') as f:
                try:
                    f.write(str(message) + '\n')
                except UnicodeEncodeError:
                    f.write(f'WRN@{now()}: A UnicodeEncodeError occurred trying to write a message log.\n')
        except:
            print('Something went very wrong trying to log a message.')
    return


def order(x, count=0):
    """Returns the base 10 order of magnitude of a number"""
    if x / 10 >= 1:
        count += order(x / 10, count) + 1
    return count


def get_item(iterable_or_dict, index, default=None):
    """Return iterable[index] or default if IndexError is raised."""
    try:
        return iterable_or_dict[index]
    except (IndexError, KeyError):
        return default

def mem_is_in_corp(member: discord.Member):
    corp = member.guild.get_role(corp_tag_id)
    corp_shield = member.guild.get_role(corp_shield_tag_id)
    return corp in member.roles or corp_shield in member.roles

# For user info
@dataclass
class UserInfo:
    id: int
    name: str = 'null'
    count: int = 0

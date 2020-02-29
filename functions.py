import datetime
import json
from attr import dataclass

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
recruiter_role = 376500752203644928
corp_tag_id = 92031682596601856
registration_channel = 204841604522049536
log_channel = 272278325244723200  # 666816919399170049 in testing server
div_req_notif_ch = 'recruitment'

# The default URL for RSI profiles
DEFAULT_RSI_URL = 'https://robertsspaceindustries.com'
profiles_url = 'https://robertsspaceindustries.com/citizens/'

# Some registration messages
timeout_msg = 'You took too long to respond. You will need to start the command over again if you wish to continue' \
              ' your application.'
get_a_person = "Okay, let me wake up the team in the Office. Depending on timezones, we'll see who we can get..."
welcome_david_msg = "Hi, I'm David. \nWelcome {author} to the Corporation! I'm your friendly neighborhood robot and" \
                    " I'll try my best to walk you through our process. \nIf you're ready to begin, " \
                    "**__please type__** \n```\nok```\nOr, if at any stage this seems too difficult, type `help` and " \
                    "I'll get a real person, it will just take longer. "
understand_david_msg = "Great. Now I know you can understand me :smiley:\nCan you **__please post your RSI handle__**" \
                       " here? Or, if you're not sure how to that, type `how`."
help_david_msg = '@Recruiter, {} has requested a personal touch for assistance with their application.'

# The possible randomly assigned values of 'hr_rep' in the corp DB
hr_reps = ['Vyryn', 'RotorBoy', 'Revoxxer', 'Chippy_X', 'ChrispyKoala', 'DARTHEDDEUS', 'Mog_No_1']

# The number of seconds to wait to time out the registration process from inactivity
timeout = 1800

# The bot randomly selects one of these statuses at startup
statuses = ["Being an adult is just walking around wondering what you're forgetting.",
            'A clean house is the sign of a broken computer.',
            "I have as much authority as the Pope, i just don't have as many people who believe it.",
            'A conclusion is the part where you got tired of thinking.',
            'To the mathematicians who thought of the idea of zero, thanks for nothing!',
            'My job is secure. No one else wants it.',
            "If at first you don't succeed, we have a lot in common.",
            'I think we should get rid of democracy. All in favor raise your hand.']
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


# Update the memory bot_commanders dict by reading from file
def set_commanders():
    global bot_commanders
    bot_commanders = load_json_var('auths')
    bot_commanders["125449182663278592"] = 10
    return


# Return the bot_commanders dict
def get_commanders():
    global bot_commanders
    return bot_commanders


# Return the poll_ids dict
def get_polls():
    global poll_ids
    return poll_ids


# Return the apikeys dict
def get_apikeys():
    global apikeys
    return apikeys


# Update the memory apikeys dict by reading from file
def set_apikeys():
    global apikeys
    apikeys = load_json_var('apikeys')
    return


# Update the memory poll_ids dict by reading from file
def set_polls():
    global poll_ids
    poll_ids = load_json_var('polls')


# Save poll_ids to file
def save_polls():
    global poll_ids
    write_json_var('polls', poll_ids)
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


# Returns the bot prefix for the guild the message is within, or the global default prefix
def get_prefix(bot, message):
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


# For user info
@dataclass
class UserInfo:
    id: int
    name: str = 'null'
    count: int = 0

import asyncio
import random
from collections import Counter

import aiohttp
import discord
from discord.ext import commands
from cogs.database import adduser, get_rsi
from functions import now, today, auth, corp_tag_id, registration_channel, log_channel, DEFAULT_RSI_URL, profiles_url, \
    timeout_msg, get_a_person, timeout as deltime, hr_reps, get_item, div_req_notif_ch, welcome_david_msg, \
    understand_david_msg, help_david_msg, recruiter_role, visitor_role, div_alternative_names, divs, div_pic
import re as _re
import requests as _requests
from bs4 import BeautifulSoup as _bs

session = aiohttp.ClientSession()


def fetch_citizen(name, url=DEFAULT_RSI_URL, endpoint='/citizens', skip_orgs=False):
    result = {}
    url = url.rstrip('/')
    citizen_url = "{}/{}/{}".format(url.rstrip('/'), endpoint.strip('/'), name)
    orgapiurl = '{}/{}'.format(url.rstrip('/'), 'api/orgs/getOrgMembers')

    page = _requests.get(citizen_url, headers=None)
    print(page)
    if page.status_code == 404:
        print(f'Received a 404 Error Code from query to {citizen_url}.')
    if page.status_code == 200:
        soup = _bs(page.text, features='lxml')
        _ = [_.text for _ in soup.select(".info .value")[:3]]
        result['username'] = get_item(_, 0, '')
        result['handle'] = get_item(_, 1, '')
        result['title'] = get_item(_, 2, '')
        result['title_icon'] = get_item(soup.select(".info .icon img"), 0, '')
        if result['title_icon']:
            result['title_icon'] = '{}/{}'.format(url, result['title_icon']['src'])
        result['avatar'] = "{}/{}".format(url, soup.select('.profile .thumb img')[0]['src'].lstrip('/'))
        result['url'] = citizen_url

        if soup.select('.profile-content .bio'):
            result['bio'] = soup.select('.profile-content .bio')[0].text.strip('\nBio').strip()
        else:
            result['bio'] = ''
        result['citizen_record'] = soup.select('.citizen-record .value')[0].text
        try:
            result['citizen_record'] = int(result['citizen_record'][1:])
        except:
            print('Encountered unexpceted citizen_record. Making citizen_record 1000000000.')
            result['citizen_record'] = 1000000000
            pass

        _ = {_.select_one('span').text:
                 _re.sub(r'\s+', ' ', _.select_one('.value').text.strip()).replace(' ,', ',')
             for _ in soup.select('.profile-content > .left-col .entry')}
        result['enlisted'] = get_item(_, 'Enlisted', '')
        result['location'] = get_item(_, 'Location', '')
        result['languages'] = get_item(_, 'Fluency', '')
        result['languages'] = result['languages'].replace(',', '').split()

        if not skip_orgs:
            orgs_page = _requests.get("{}/organizations".format(citizen_url))
            if orgs_page.status_code == 200:
                orgsoup = _bs(orgs_page.text, features='lxml')
                result['orgs'] = []
                for org in orgsoup.select('.orgs-content .org'):
                    orgname, sid, rank = [_.text for _ in org.select('.info .entry .value')]
                    if orgname[0] == '\xa0':
                        orgname = sid = rank = 'REDACTED'

                    roles = []
                    r = _requests.post(orgapiurl, data={'symbol': sid, 'search': name})
                    if r.status_code == 200:
                        r = r.json()
                        if r['success'] == 1:
                            apisoup = _bs(r['data']['html'], features='lxml')
                            roles = [_.text for _ in apisoup.select('.rolelist .role')]

                    orgdata = {
                        'name': orgname,
                        'sid': sid,
                        'rank': rank,
                        'roles': roles,
                    }
                    try:
                        orgdata['icon'] = '{}/{}'.format(url, org.select('.thumb img')[0]['src'].lstrip('/'))
                    except IndexError:
                        pass

                    result['orgs'].append(orgdata)
    return result


def check_ok(author):
    def in_check(message):
        return message.author == author and (
                'ok'.casefold() in message.content.casefold() or 'help'.casefold() in message.content.casefold())

    return in_check


def check_author(author):
    def in_check(message):
        return message.author == author

    return in_check


class Corp(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # Events
    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Cog {self.qualified_name} is ready.')

    def cog_unload(self):
        print("Closing Corp cog...")
        session.close()

    # Commands
    @commands.command(name='register', description='Register for The Corporation!')
    async def corp_register(self, ctx):
        """
        Register for the Corporation!
        """
        # If already registered, don't let them register again
        if ctx.guild.get_role(667268366456717332) in ctx.author.roles or ctx.guild.get_role(
                corp_tag_id) in ctx.author.roles:
            await ctx.send('It looks like you already have a Corporateer tag.')
            return

        # Make sure they understand
        await ctx.send(welcome_david_msg.format(author=ctx.author.mention))
        try:
            response = await self.bot.wait_for('message', check=check_ok(ctx.author), timeout=deltime)
        except asyncio.TimeoutError:
            await ctx.send(timeout_msg)
            return
        if response.content.casefold() == 'help'.casefold():
            await ctx.guild.get_channel(log_channel).send(help_david_msg.format(ctx.author))
            await ctx.send(get_a_person)
            return
        # Get RSI handle, can get link from this.
        flag = False
        handle_e = ""
        while not flag:
            await ctx.send(
                content=understand_david_msg)
            try:
                rsi_handle = await self.bot.wait_for('message', check=check_author(ctx.author), timeout=deltime)
            except asyncio.TimeoutError:
                await ctx.send(timeout_msg)
                return
            if response.content.casefold() == 'help'.casefold():
                await ctx.guild.get_channel(log_channel).send(
                    f'@Recruiter, {ctx.author} has requested a personal touch '
                    f'for assistance with their application.')
                await ctx.send(get_a_person)
                return
            if rsi_handle.content.casefold() == 'how'.casefold():
                await ctx.send("\n\n\nHere's a more detailed description of how to do that.\n```\n"
                               f"1)  Go to https://robertsspaceindustries.com\n"
                               f"2)  Log in to your account.\n"
                               f"3)  Find and click the Account button in the top right.\n"
                               f"4)  Copy the large/top name beside your picture, and paste it as a reply here.\n```"
                               f"As an example, for someone with the RSI handle `Vyryn`, it would look something like"
                               f" this:",
                               file=discord.File('rsi_register_helper_image.png'))
                await ctx.send("When you're ready, please post your RSI handle here.")
                try:
                    rsi_handle = await self.bot.wait_for('message', check=check_author(ctx.author), timeout=deltime)
                except asyncio.TimeoutError:
                    await ctx.send(timeout_msg)
                    return
                if rsi_handle.content.casefold() == 'help'.casefold():
                    await ctx.guild.get_channel(log_channel).send(
                        f'@Recruiter, {ctx.author} has requested a personal touch '
                        f'for assistance with their application.')
                    await ctx.send(get_a_person)
                    return
            handle_e = rsi_handle.content
            # Confirm RSI handle
            flag2 = False
            while not flag2:
                await ctx.send(f"I'd just like to confirm: Your RSI handle is   **`{handle_e}`**   ?\n"
                               f"**__Confirm with__** \n```\nok```\n, or type it again if you made a mistake.")
                try:
                    response = await self.bot.wait_for('message', check=check_author(ctx.author), timeout=deltime)
                except asyncio.TimeoutError:
                    await ctx.send(timeout_msg)
                    return
                if response.content.casefold() == 'help'.casefold():
                    await ctx.guild.get_channel(log_channel).send(
                        f'@Recruiter, {ctx.author} has requested a personal touch '
                        f'for assistance with their application.')
                    await ctx.send(get_a_person)
                    return
                if response.content.casefold() == 'ok'.casefold():
                    flag = True
                    flag2 = True
                else:
                    split = response.content.split('/')
                    handle_e = split[len(split) - 1]
        # Confirm profile is theirs
        # one_time_code = random.randint(min_rand, min_rand * 10)
        await ctx.send(
            content=f"Great. Next I need to check your profile actually belongs to you.\n The way I'd like to do "
                    f"that is by having you **__add the phrase__** \n\nI am {ctx.author} on Discord\n\n**__ to your"
                    f" RSI profile__** and then type `ok` and I'll take a look at your profile. Or, "
                    f"if you're not sure how to do that, **__type__** `how`.")
        try:
            response = await self.bot.wait_for('message', check=check_author(ctx.author), timeout=deltime)
        except asyncio.TimeoutError:
            await ctx.send(timeout_msg)
            return
        if response.content.casefold() == 'help'.casefold():
            await ctx.guild.get_channel(log_channel).send(f'@Recruiter, {ctx.author} has requested a personal touch '
                                                          f'for assistance with their application.')
            await ctx.send(get_a_person)
            return
        if response.content.casefold() == 'how'.casefold():
            await ctx.send(
                content=f"Here's a more detailed description of how to do that.\n```\n"
                        f"1) Go to https://robertsspaceindustries.com/account/profile and scroll down to where it says 'Short Bio'\n"
                        f"2) Add 'I am {ctx.author} on Discord.' to the 'Short Bio' and then Click 'APPLY ALL CHANGES'\n"
                        f"3) Check that you are in The Corporation on RSI and it is visible on your profile.\n"
                        f"4) Tell me 'ok' and I'll check your profile.```",
                file=discord.File('rsi_register_helper_image_2.png'))
            try:
                ok_check = await self.bot.wait_for('message', check=check_ok(ctx.author), timeout=deltime)
            except asyncio.TimeoutError:
                await ctx.send(timeout_msg)
                return
        await ctx.send(f"Checking your RSI profile...")
        citizen = fetch_citizen(handle_e)
        print(citizen)
        # await ctx.send("Here's what I found.")
        message = ""
        ready = False
        try:
            bio = citizen['bio']
        except KeyError:
            await ctx.send("Hmm, I wasn't able to find your profile. **__Are you sure you spelled your handle "
                           "correctly?__** Please double check and try this command again. It is also possible the "
                           "RSI site is down for the moment, try again in a few minutes.")
            return
        orgnames = [i['name'] for i in citizen['orgs']]
        if f'I am {ctx.author}' in citizen['bio'] and citizen['handle'].casefold() == handle_e.casefold() and \
                'The Corporation' in orgnames:
            message += "Great news! I was able to confirm you put the phrase in your bio *and* that you are in the" \
                       " Corporation. I'll go ahead and assign your Corporateer tag."
            ready = True
        else:
            if citizen['handle'].casefold() == handle_e.casefold():
                message += "Good news. I was able to find your profile. "
                flag = True
            else:
                message += "Hmm, I wasn't able to find your profile. **__Are you sure you spelled your handle " \
                           "correctly?__** Please double check and try again."
            if 'The Corporation' in orgnames:
                if flag:
                    message += "Plus, "
                else:
                    message += "Good news. "
                message += "I was able to confirm you're in The Corporation. "
                flag2 = True
            else:
                message += "I wasn't able to confirm you're in The Corporation. **__Please make sure The " \
                           "Corporation is set as your main org and visible__**, and try again. "
            if f'I am {ctx.author}' in citizen['bio']:
                if not flag and not flag2:
                    message += "Good news. "
                else:
                    message += "Plus, "
                message += "I was able to find the phrase in your bio. "
            else:
                message += f"I wasn't able to find `I am {ctx.author} on Discord.` in your bio. **__Please add that" \
                           f" to your bio and then re-run this command.__** "
        await ctx.send(message)
        # Yay! Feedback time
        hr_rep = "N/A"
        if ready:
            joined = now()
            rsi_number = citizen['citizen_record']
            languages = citizen.get('languages', '')
            location = citizen.get('location', '')
            joined_rsi = citizen['enlisted']
            hr_rep = random.choice(hr_reps)
            adduser(ctx.author, handle_e, languages, location, joined_rsi, rsi_number, joined, hr_rep)
            # Get display name so it can be changed to RSI name.
            disp = None
            if ctx.author.nick is not None:
                disp = ctx.author.nick
            else:
                disp = ctx.author.display_name
            try:
                await ctx.author.add_roles(ctx.guild.get_role(corp_tag_id))
                if ctx.guild.get_role(visitor_role) in ctx.author.roles:
                    await ctx.author.remove_roles(ctx.guild.get_role(visitor_role))
                    await ctx.send(f'Removed {ctx.author}\'s @Visitor role.', delete_after=10)
                if disp != handle_e:
                    await ctx.author.edit(reason='Bot change to match RSI handle', nick=handle_e)
                    await ctx.send('I have changed your nickname on this server to match your RSI handle so that games'
                                   ' nights can be done more easily.')
            except PermissionError:
                await ctx.send("Hmm, the bot seems to be configured incorrectly. Make sure I have all required perms "
                               "and my role is high enough in the role list.")
            message = f"\n\nNearly done... I hope you enjoyed this process. If you have any **__feedback__** for the" \
                      f" HR team, type it now and I'll convey it. Otherwise, you can just type `ok` or `no` to finish" \
                      f" up."
        else:
            await ctx.send(f"I'm sorry you weren't able to complete the process this time. When you're ready to try" \
                           f" again, use `^register` again.")
            return
        await ctx.send(message)
        try:
            feedback = await self.bot.wait_for('message', check=check_author(ctx.author), timeout=deltime)
        except asyncio.TimeoutError:
            pass
        if not ready:
            return
        if feedback.content.casefold() == 'help'.casefold():
            await ctx.guild.get_channel(log_channel).send(f'@Recruiter, {ctx.author} has requested a personal touch '
                                                          f'for assistance with their application.')
            await ctx.send(get_a_person)
            return
        await ctx.send(
            content=f"Welcome! Enjoy your time here at Corp. Your HR rep is `{hr_rep}`. If you"
                    f" have any questions I'm not able to answer, please do contact them. This is our new members "
                    f"guide, it may be of use to you. Read at your leisure. :smiley:",
            file=discord.File('New_Members_Guide_V2.1.pdf'))
        await ctx.send("The next step is to join some divisions. Much of the content of the Corporation is hidden and"
                       " visible only to division members. You can choose one or several that you are interested in."
                       " When you're ready to join some divisions, type `^reqdiv division`. Be sure to do so to see "
                       "all the fun content!")
        await ctx.send("If you'd like some training, type `^trainme` to let our trainers know you want to participate"
                       " in the next M1 training session.")

        # Log for HR/bookkeeping
        await self.bot.get_channel(registration_channel).send(
            f"**{ctx.author.mention}** has successfully become a Corporateer at {now()}. Their RSI link is:\n"
            f"```{profiles_url + rsi_handle.content}```")
        embed = discord.Embed(title='New Corporateer!', description='', color=ctx.author.color)
        embed.add_field(name="User:", value=ctx.author.mention, inline=False)
        embed.add_field(name="Citizen Number #", value=citizen['citizen_record'], inline=False)
        embed.add_field(name="RSI URL:", value=profiles_url + rsi_handle.content, inline=False)
        embed.add_field(name="Languages:", value=f"{citizen['languages']}.", inline=False)
        embed.add_field(name="Location:", value=f"{citizen['location']}.", inline=False)
        embed.add_field(name="Joined CORP:", value=joined, inline=False)
        embed.add_field(name="Joined RSI:", value=citizen['enlisted'], inline=False)
        embed.add_field(name="Assigned HR Rep:", value=hr_rep, inline=False)
        app = await self.bot.get_channel(log_channel).send(content=None, embed=embed)
        # str(feedback.content)
        await self.bot.get_channel(log_channel).send(f"They had the following feedback:\n```"
                                                     f"{feedback.content}```"
                                                     f"\nHuman Resources, please give them a warm welcome in #lobby "
                                                     f"then mark this post with :corpyes:\n "
                                                     f"{ctx.guild.get_role(recruiter_role).mention}, please verify "
                                                     f"this user hasn't registered in the past, and use `^remove_corp`"
                                                     f" if their Corporateer tag needs removing.")

    @commands.command(name='checkrsi', aliases=['fetch_cit, rsi'], description='Check citizen\'s rsi profile')
    async def fetch_citizen_cmd(self, ctx, user):
        """
        Check someone's RSI profile
        """
        if isinstance(user, discord.User):
            name = user.name
            if user.nick is not None:
                name = user.nick
        else:
            name = user
        citizen = fetch_citizen(name)
        print(citizen)
        await ctx.send(f'{DEFAULT_RSI_URL}/citizens/{name}')
        pass

    @commands.command(name='listlinks', description='List all the RSI links for everyone in your voice chat.')
    async def list_rsi_links(self, ctx, *, channel=None):
        """
        Print a list of the RSI handles of everyone in the selected voice channel.
        """
        if channel is None:
            if ctx.author.voice is None or ctx.author.voice.channel is None:
                await ctx.send(f"{ctx.author}, you aren't currently in a voice channel. Either join one or specify "
                               f"one with the command.")
                return
            else:
                channel = ctx.author.voice.channel
        else:
            for try_channel in ctx.guild.voice_channels:
                if try_channel.name.casefold() == channel.casefold():
                    channel = try_channel
                    break
        try:
            if len(channel.members) < 1:
                await ctx.send(f'I see no one in that channel.')
                return
        except AttributeError:
            await ctx.send('It looks like you may have misspelled that channel name. Try again.')
            return
        members = []
        for member in channel.members:
            link = get_rsi(member.id)
            rsi = link[link.rfind('/') + 1:len(link)]
            members.append((rsi, str(member), link))
        members = sorted(members)
        message = ['']
        i = 0
        for member in members:
            try:
                message[int(i / 10)] += f'I see {member[1]} in that channel, their link is {member[2]}.\n'
            except IndexError:
                message.append('')
                message[int(i / 10)] += f'I see {member[1]} in that channel, their link is {member[2]}.\n'
            i += 1
        for mes in message:
            await ctx.send(mes)

    @commands.command(name='listdivs', description='List all the divisons of members in your voice channel or target voice channel.')
    async def list_divs(self, ctx, num=0, *, channel=None):
        """
        Print a list of the division tags of everyone in the selected voice channel. Add a number to list the top that many, defaults to 10.
        """
        if num < 1:
            num = 10
        if channel is None:
            if ctx.author.voice is None or ctx.author.voice.channel is None:
                await ctx.send(f"{ctx.author}, you aren't currently in a voice channel. Either join one or specify "
                               f"one with the command.")
                return
            else:
                channel = ctx.author.voice.channel
        else:
            for try_channel in ctx.guild.voice_channels:
                if try_channel.name.casefold() == channel.casefold():
                    channel = try_channel
                    break
        try:
            if len(channel.members) < 1:
                await ctx.send(f'I see no one in that channel.')
                return
        except AttributeError:
            await ctx.send('It looks like you may have misspelled that channel name. Try again.')
            return
        divs_in_channel = Counter()
        for member in channel.members:
            for div in member.roles:
                if div.name.casefold() in divs.keys():
                    divs_in_channel[div.name] += 1
        print(divs_in_channel)
        print((divs_in_channel.most_common(num)))
        message = ''
        counter = 0
        for div in divs_in_channel.most_common(num):
            counter += 1
            message += f'{counter})  {div[1]} x {div[0]}\n'
        await ctx.send(f'I found the following divs:\n{message}')


    @commands.command(name='reqdiv', description='Request a division tag for any division or divisions')
    async def reqdiv(self, ctx, *, div):
        """
        Request a division tag for any divs in divs
        """
        # If not yet registered, don't allow use of reqdiv
        if not ctx.guild.get_role(corp_tag_id) in ctx.author.roles:
            await ctx.send('I\'m sorry, you need to get a Corporateer tag first. Use `^register`.')
            return
        # Find reporting channel
        for channel in ctx.guild.channels:
            if channel.name.casefold() == div_req_notif_ch.casefold():
                management = channel
        div = div_alternative_names.get(div.casefold(), div)
        dept = divs.get(div.casefold(), 'none')
        # If not a valid division
        if dept == 'none':
            await ctx.send(
                f"Hmm, I didn't find {div} in our list of divisions. Our divisions are all in the picture below.\n"
                f"{div_pic}")
            return
        print(f'{ctx.author} used reqdiv to request to join {div} at {now()}.')
        # Find DH and DL roles
        for role in ctx.guild.roles:
            if role.name.casefold() == f'DL {div.casefold()}'.casefold():
                dl_role = role
            elif role.name.casefold() == f'DH {divs[div.casefold()].casefold()}'.casefold():
                dh_role = role
        await management.send(f'{dl_role.mention}, {dh_role.mention}, {ctx.author} is interested in joining {div}! '
                              f'Please contact them at your convenience to help them with that.')
        await ctx.send(f"Okay, I have informed the division leader and department head that you're interested "
                       f"in joining {div}.")

    @commands.command(name='adduser', description='Adds a user to the database.')
    @commands.check(auth(1))
    async def adduser(self, ctx, user: discord.User, rsi):
        """
        Insert a user into the users database
        Requires Auth 1
        """
        citizen = fetch_citizen(rsi)
        joined = now()
        try:  # can check if the citizen call was valid by trying to get the first key from it
            rsi_number = citizen['citizen_record']
        except KeyError:
            await ctx.send('I think you mis-typed their rsi handle. Contact Vyryn if this issue persists.')
            return
        languages = citizen['languages']
        location = citizen['location']
        joined_rsi = citizen['enlisted']
        hr_rep = random.choice(hr_reps)
        result = adduser(user, rsi, languages, location, joined_rsi, rsi_number, joined, hr_rep)
        await ctx.send(result)
        print(result)

    @commands.command(name='remove_corp', description='Removes someone\'s Corporateer tag')
    @commands.check(auth(1))
    async def remove_corp(self, ctx, user: discord.Member):
        """
        Removes a corporateer tag. Requires Auth 1.
        """
        try:
            await user.remove_roles(ctx.guild.get_role(corp_tag_id))
            print(f'Removed corp tag from {user} by request from {ctx.author}.')
            await ctx.send(f'Removed corp tag from {user} by request from {ctx.author}.')
        except PermissionError:
            await ctx.send("Hmm, the bot seems to be configured incorrectly. Make sure I have all required perms "
                           "and my role is high enough in the role list.")


def setup(bot):
    bot.add_cog(Corp(bot))

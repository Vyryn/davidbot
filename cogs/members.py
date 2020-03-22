import random

import discord
from discord.ext import commands

from cogs.corp import corp_tag_id, check_ok, check_author, fetch_citizen
from cogs.database import adduser
from functions import basicperms, sigperms, deltime, embed_footer, now, log_channel, ping_role, recruiter_role, \
    candidate_role, welcome_david_msg, timeout_msg, help_david_msg, get_a_person, understand_david_msg, hr_reps, \
    visitor_role, registration_channel, profiles_url


class Members(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Events
    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Cog {self.qualified_name} is ready.')

    @commands.Cog.listener()
    @commands.guild_only()
    async def on_member_join(self, member: discord.Member):
        embed = discord.Embed(title='', description='', color=discord.Color.teal())
        embed.set_author(icon_url=member.avatar_url, name=f'{member} ({member.id}')
        embed.set_footer(text=f'User Joined • {now()}')
        await member.guild.get_channel(log_channel).send('@here', embed=embed)
        print(f'{member.display_name} ({member.mention}) has joined {member.guild}.')

        """
            Register for the Corporation!
        """
        # If already registered, don't let them register again
        # Make sure they understand
        await member.send(welcome_david_msg.format(author=member.mention))
        try:
            response = await self.bot.wait_for('message', check=check_ok(member), timeout=deltime)
        except TimeoutError:
            await member.send(timeout_msg)
            return
        if response.content.casefold() == 'help'.casefold():
            await member.guild.get_channel(log_channel).send(help_david_msg.format(member))
            await member.send(get_a_person)
            return
        # Get RSI handle, can get link from this.
        flag = False
        handle_e = ""
        while not flag:
            await member.send(
                content=understand_david_msg)
            try:
                rsi_handle = await self.bot.wait_for('message', check=check_author(member), timeout=deltime)
            except TimeoutError:
                await member.send(timeout_msg)
                return
            if response.content.casefold() == 'help'.casefold():
                await member.guild.get_channel(log_channel).send(
                    f'{member.guild.get_role(recruiter_role).mention()}, {member.mention} has requested a personal touch '
                    f'for assistance with their application.')
                await member.send(get_a_person)
                return
            if rsi_handle.content.casefold() == 'how'.casefold():
                await member.send("\n\n\nHere's a more detailed description of how to do that.\n```\n"
                                  f"1)  Go to https://robertsspaceindustries.com\n"
                                  f"2)  Log in to your account.\n"
                                  f"3)  Find and click the Account button in the top right.\n"
                                  f"4)  Copy the large/top name beside your picture, and paste it as a reply here.\n```"
                                  f"As an example, for someone with the RSI handle `Vyryn`, it would look something like"
                                  f" this:",
                                  file=discord.File('rsi_register_helper_image.png'))
                await member.send("When you're ready, please post your RSI handle here.")
                try:
                    rsi_handle = await self.bot.wait_for('message', check=check_author(member), timeout=deltime)
                except TimeoutError:
                    await member.send(timeout_msg)
                    return
                if rsi_handle.content.casefold() == 'help'.casefold():
                    await member.guild.get_channel(log_channel).send(
                        f'{member.guild.get_role(recruiter_role).mention()}, {member.mention} has requested a personal touch '
                        f'for assistance with their application.')
                    await member.send(get_a_person)
                    return
            handle_e = rsi_handle.content
            # Confirm RSI handle
            flag2 = False
            while not flag2:
                await member.send(f"I'd just like to confirm: Your RSI handle is   **`{handle_e}`**   ?\n"
                                  f"**__Confirm with__** \n```\nok```\n, or type it again if you made a mistake.")
                try:
                    response = await self.bot.wait_for('message', check=check_author(member), timeout=deltime)
                except TimeoutError:
                    await member.send(timeout_msg)
                    return
                if response.content.casefold() == 'help'.casefold():
                    await member.guild.get_channel(log_channel).send(
                        f'{member.guild.get_role(recruiter_role).mention()}, {member} has requested a personal touch '
                        f'for assistance with their application.')
                    await member.send(get_a_person)
                    return
                if response.content.casefold() == 'ok'.casefold():
                    flag = True
                    flag2 = True
                else:
                    split = response.content.split('/')
                    handle_e = split[len(split) - 1]
        # Confirm profile is theirs
        # one_time_code = random.randint(min_rand, min_rand * 10)
        await member.send(
            content=f"Great. Next I need to check your profile actually belongs to you.\n The way I'd like to do "
                    f"that is by having you **__add the phrase__** \n\nI am {member} on Discord\n\n**__ to your"
                    f" RSI profile__** and then type `ok` and I'll take a look at your profile. Or, "
                    f"if you're not sure how to do that, **__type__** `how`.")
        try:
            response = await self.bot.wait_for('message', check=check_author(member), timeout=deltime)
        except TimeoutError:
            await member.send(timeout_msg)
            return
        if response.content.casefold() == 'help'.casefold():
            await member.guild.get_channel(log_channel).send(
                f'{member.guild.get_role(recruiter_role).mention()}, {member} has requested a personal touch '
                f'for assistance with their application.')
            await member.send(get_a_person)
            return
        if response.content.casefold() == 'how'.casefold():
            await member.send(
                content=f"Here's a more detailed description of how to do that.\n```\n"
                        f"1) Go to https://robertsspaceindustries.com/account/profile and scroll down to where it says"
                        f" 'Short Bio'\n"
                        f"2) Add 'I am {member} on Discord.' to the 'Short Bio' and then Click 'APPLY ALL CHANGES'\n"
                        f"3) Check that you are in The Corporation on RSI and it is visible on your profile.\n"
                        f"4) Tell me 'ok' and I'll check your profile.```",
                file=discord.File('rsi_register_helper_image_2.png'))
            try:
                ok_check = await self.bot.wait_for('message', check=check_ok(member), timeout=deltime)
            except TimeoutError:
                await member.send(timeout_msg)
                return
        await member.send(f"Checking your RSI profile...")
        citizen = fetch_citizen(handle_e)
        print(citizen)
        # await ctx.send("Here's what I found.")
        message = ""
        ready = False
        try:
            bio = citizen['bio']
        except KeyError:
            await member.send("Hmm, I wasn't able to find your profile. **__Are you sure you spelled your handle "
                              "correctly?__** Please double check and try this command again. It is also possible the "
                              "RSI site is down for the moment, try again in a few minutes.")
            return
        orgnames = [i['name'] for i in citizen['orgs']]
        if f'I am {member}' in citizen['bio'] and citizen['handle'].casefold() == handle_e.casefold() and \
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
            if f'I am {member}' in citizen['bio']:
                if not flag and not flag2:
                    message += "Good news. "
                else:
                    message += "Plus, "
                message += "I was able to find the phrase in your bio. "
            else:
                message += f"I wasn't able to find `I am {member} on Discord.` in your bio. **__Please add that" \
                           f" to your bio and then re-run this command.__** "
        await member.send(message)
        # Yay! Feedback time
        hr_rep = "N/A"
        if ready:
            joined = now()
            rsi_number = citizen['citizen_record']
            languages = citizen.get('languages', '')
            location = citizen.get('location', '')
            joined_rsi = citizen['enlisted']
            hr_rep = random.choice(hr_reps)
            adduser(member, handle_e, languages, location, joined_rsi, rsi_number, joined, hr_rep)
            try:
                await member.add_roles(member.guild.get_role(corp_tag_id))
                if visitor_role in member.roles:
                    await member.remove_roles(visitor_role)
                    await member.send(f'Removed {member}\'s @Visitor role.')
            except PermissionError:
                await member.send("Hmm, the bot seems to be configured incorrectly. Make sure I have all required "
                                  "perms and my role is high enough in the role list.")
            message = f"\n\nNearly done... I hope you enjoyed this process. If you have any **__feedback__** for the" \
                      f" HR team, type it now and I'll convey it. Otherwise, you can just type `ok` or `no` to finish" \
                      f" up."
        else:
            await member.send(f"I'm sorry you weren't able to complete the process this time. When you're ready to "
                              f"try again, use `^register` again.")
            return
        await member.send(message)
        try:
            feedback = await self.bot.wait_for('message', check=check_author(member), timeout=deltime)
        except TimeoutError:
            pass
        if not ready:
            return
        if feedback.content.casefold() == 'help'.casefold():
            await member.guild.get_channel(log_channel).send(
                f'{member.guild.get_role(recruiter_role).mention()}, {member} has requested a personal touch '
                f'for assistance with their application.')
            await member.send(get_a_person)
            return
        await member.send(
            content=f"Welcome! Enjoy your time here at Corp. Your HR rep is `{hr_rep}`. If you"
                    f" have any questions I'm not able to answer, please do contact them. This is our new members "
                    f"guide, it may be of use to you. Read at your leisure. :smiley:",
            file=discord.File('New_Members_Guide_V2.1.pdf'))
        await member.send(
            "The next step is to join some divisions. Much of the content of the Corporation is hidden and"
            " visible only to division members. You can choose one or several that you are interested in."
            " When you're ready to join some divisions, type `^reqdiv division`. Be sure to do so to see "
            "all the fun content!")
        await member.send(
            "If you'd like some training, type `^trainme` to let our trainers know you want to participate"
            " in the next M1 training session.")

        # Log for HR/bookkeeping
        await self.bot.get_channel(registration_channel).send(
            f"**{member.mention}** has successfully become a Corporateer at {now()}. Their RSI link is:\n"
            f"```{profiles_url + rsi_handle.content}```")
        embed = discord.Embed(title='New Corporateer!', description='', color=member.color)
        embed.add_field(name="User:", value=member.mention, inline=False)
        embed.add_field(name="Citizen Number #", value=citizen['citizen_record'], inline=False)
        embed.add_field(name="RSI URL:", value=profiles_url + rsi_handle.content, inline=False)
        embed.add_field(name="Languages:", value=f"{citizen['languages']}.", inline=False)
        embed.add_field(name="Location:", value=f"{citizen['location']}.", inline=False)
        embed.add_field(name="Joined CORP:", value=joined, inline=False)
        embed.add_field(name="Joined RSI:", value=citizen['enlisted'], inline=False)
        embed.add_field(name="Assigned HR Rep:", value=hr_rep, inline=False)
        app = await self.bot.get_channel(log_channel).send(content=None, embed=embed)
        await self.bot.get_channel(log_channel).send(f"They had the following feedback:\n```{feedback.content}```\n"
                                                     f"Human Resources, please give them a warm welcome in #lobby "
                                                     f"then mark this post with :corpyes:\n "
                                                     f"{member.guild.get_role(recruiter_role).mention()}, please verify"
                                                     f" this user hasn't registered in the past, and use `^remove_corp`"
                                                     f" if their Corporateer tag needs removing.")

    @commands.Cog.listener()
    @commands.guild_only()
    async def on_member_remove(self, member: discord.Member):
        if member.guild.get_role(corp_tag_id) in member.roles:
            embed = discord.Embed(title='', description='', color=discord.Color.gold())
            embed.set_author(icon_url=member.avatar_url, name=f'{member} ({member.id}')
            embed.set_footer(text=f'Corporateer Left • {now()}')
            await member.guild.get_channel(log_channel).send('@here', embed=embed)
            print(f'{member.display_name} ({member.mention}) has left {member.guild}.')
        else:
            embed = discord.Embed(title='', description='', color=discord.Color.gold())
            embed.set_author(icon_url=member.avatar_url, name=f'{member} ({member.id}')
            embed.set_footer(text=f'User Left • {now()}')
            await member.guild.get_channel(log_channel).send(embed=embed)
            print(f'{member.display_name} ({member.mention}) has left {member.guild}.')

    # List out the perms of a member
    @commands.command(name='perms', aliases=['permissions', 'checkperms', 'whois', 'perm'], description='Who dat?')
    @commands.guild_only()
    async def check_permissions(self, ctx, member: discord.Member = None, detail=1):
        """Check the permissions of a user on the current server
                Member: The person who's perms to check
                Detail: 1 for significant perms, 2 for notable perms, 3 for all perms"""
        # assign caller of command if no one is chosen
        if not member:
            member = ctx.author

        # embed it
        embed = discord.Embed(title='', description='', color=member.color)
        embed.set_author(icon_url=member.avatar_url, name=f"{str(member)}'s perms on {ctx.guild.name}")
        if detail > 0:  # include basic perms
            iperms = '\n'.join(perm for perm, value in member.guild_permissions if str(perm) in basicperms if value)
            if len(iperms) < 1:
                iperms += 'None'
            embed.add_field(name='Important Perms:', value=iperms)
        else:
            embed.add_field(name='There was an error.', value='Error')
        if detail > 1:  # include notable perms
            nperms = '\n'.join(perm for perm, value in member.guild_permissions if str(perm) in sigperms if value)
            if len(nperms) < 1:
                nperms += 'None'
            embed.add_field(name='Notable Perms:', value=nperms)
        if detail > 2:  # include the rest of the perms
            perms = '\n'.join(perm for perm, value in member.guild_permissions if str(perm) not in (basicperms +
                                                                                                    sigperms) if value)
            if len(perms) < 1:
                perms += 'None'
            embed.add_field(name='Other Perms:', value=perms)
        embed.set_footer(text=embed_footer(ctx.author))
        await ctx.send(content=None, embed=embed, delete_after=deltime * 5)
        print(f'Perms command used by {ctx.author} at {now()} on member {member} with detail {detail}.')

    # Toggle @PING role
    @commands.command(name='getpingrole', aliases=['pingme', 'noping'],
                      description='Self-assign or remove the @PING role.')
    @commands.guild_only()
    async def toggle_ping_tag(self, ctx, member: discord.Member = None):
        """
        Assign yourself the @PING tag. Requires a Corporateer tag.
        Recruiters can also assign the @PING tag to other people.
        """
        # If not yet registered, don't allow use of ping
        if not ctx.guild.get_role(corp_tag_id) in ctx.author.roles:
            await ctx.send('I\'m sorry, you need to get a Corporateer tag first. Use `^register`.')
            return
        target = ctx.author
        the_ping_role = ctx.guild.get_role(ping_role)
        # For recruiters
        if ctx.guild.get_role(recruiter_role) in ctx.author.roles and member is not None:
            target = member
        # Toggle ping role
        if the_ping_role in target.roles:
            await target.remove_roles(the_ping_role)
            await ctx.send(f'Removed {target}\'s @PING role.')
        else:
            await target.add_roles(the_ping_role)
            await ctx.send(f'Added {target}\'s @PING role.')

    # Toggle @Candidate role
    @commands.command(name='trainme', aliases=['corpup'],
                      description='Self-assign or remove the @Candidate role.')
    @commands.guild_only()
    async def toggle_candidate_tag(self, ctx, member: discord.Member = None):
        """
        Assign yourself the @Candidate tag. Requires a Corporateer tag.
        Recruiters can also assign the @Candidate tag to other people.
        """
        # If not yet registered, don't allow use of ping
        if not ctx.guild.get_role(corp_tag_id) in ctx.author.roles:
            await ctx.send('I\'m sorry, you need to get a Corporateer tag first. Use `^register`.')
            return
        target = ctx.author
        the_candidate_role = ctx.guild.get_role(candidate_role)
        # For recruiters
        if ctx.guild.get_role(recruiter_role) in ctx.author.roles and member is not None:
            target = member
        # Toggle candidate role
        if the_candidate_role in target.roles:
            await target.remove_roles(the_candidate_role)
            await ctx.send(f'Removed {target}\'s @Candidate role.')
        else:
            await target.add_roles(the_candidate_role)
            await ctx.send(f'Added {target}\'s @Candidate role.')


def setup(bot):
    bot.add_cog(Members(bot))

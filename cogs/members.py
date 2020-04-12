import random

import discord
from discord.ext import commands

from cogs.corp import corp_tag_id, check_ok, check_author, fetch_citizen
from cogs.database import adduser
from functions import basicperms, sigperms, deltime, embed_footer, now, log_channel, ping_role, recruiter_role, \
    candidate_role, welcome_david_msg, timeout_msg, help_david_msg, get_a_person, understand_david_msg, hr_reps, \
    visitor_role, registration_channel, profiles_url, div_alternative_names


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
        # TODO

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

    # List all members in divisions you have a DL tag for
    @commands.command(name='membership', aliases=['divlist'])
    @commands.guild_only()
    async def div_membership(self, ctx, div=None):
        """
        Lists all members of divisions you have the DL tag for. Future improvements will make DH and Board tags give
        a variety of parameters.
        If you have multiple DL tags, you may need to specify which division you'd like to check.
        Requires Manager tag to use.
        """
        print(f'div_membership triggered by {ctx.author} for div {div} at {now()}.')
        # Sanitize div name
        if div is not None:
            div = div_alternative_names.get(div.casefold(), div)
        # Check for authorization and check divisions that are likely to be of interest in one loop
        manager_flag = False
        for role in ctx.author.roles:
            if str(role) == 'Manager':
                manager_flag = True
            elif div is None and str(role).startswith('DL '):
                div = str(role).split('DL ')[1]
        if not manager_flag:
            await ctx.send('A manager tag is required to use this command.')
            print('Not authorized.')
            return
        # Need to do a second loop to find the division of interest
        div_interest = None
        for role in ctx.guild.roles:
            if str(role).casefold() == div.casefold():
                div_interest = role
                break
        print(div_interest)
        # Now time for the big check
        member_count = 0
        div_members = []
        for member in ctx.guild.members:
            if div_interest in member.roles:
                print(member)
                member_count += 1
                div_members.append(member)
        # Prepare file
        upload_file_address = f'./memberships/{div}_members.txt'
        with open(upload_file_address, 'w+') as f:
            for member in div_members:
                try:
                    f.write(f'{str(member)}\n')
                except UnicodeEncodeError:
                    f.write(f'A user with non-unicode characters in their name, id: {str(member.id)}\n')
        await ctx.send(f'I found {member_count} members in {div}. Full div membership is in the attached file.',
                       file=discord.File(upload_file_address))


def setup(bot):
    bot.add_cog(Members(bot))

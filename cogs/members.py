import discord
from discord.ext import commands

from cogs.corp import corp_tag_id
from functions import basicperms, sigperms, deltime, embed_footer, now, log_channel, ping_role, recruiter_role, \
    candidate_role


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

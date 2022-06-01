import json
from discord.ext import commands
from functions import global_prefix, now


class Management(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Events
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Cog {self.qualified_name} is ready.")

    # Custom prefix upon joining guild
    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        print(f"Joined guild {guild}")
        with open("prefixes.json", "r") as f:
            prefixes = json.load(f)

        prefixes[str(guild.id)] = global_prefix

        with open("prefixes.json", "w") as f:
            json.dump(prefixes, f, indent=4)
        print(f"Bot added to server {guild} at {now()}.")

    # remove custom prefix from bot record
    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        with open("prefixes.json", "r") as f:
            prefixes = json.load(f)

        prefixes.pop(str(guild.id))

        with open("prefixes.json", "w") as f:
            json.dump(prefixes, f, indent=4)
        print(f"Bot removed from server {guild} at {now()}.")

    # change server prefix
    @commands.group(name="prefix", description="Check or change the server prefix")
    @commands.guild_only()
    async def prefix(self, ctx):
        """Check or change the server prefix
        With no parameters, tells you what the prefix is.
        Considering you need to know what the prefix is to run the command, it's very helpful, I know.
        However, /prefix set <prefix> is used to change the server prefix."""
        with open("prefixes.json", "r") as f:
            prefixes = json.load(f)
        await ctx.send(f"Prefix is {prefixes[str(ctx.guild.id)]}")
        print(f"Prefix checked by {ctx.author} at {now()} in server {ctx.guild}.")

    @prefix.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def set(self, ctx, prefix=global_prefix):
        with open("prefixes.json", "r") as f:
            prefixes = json.load(f)
        print(f"Changing {ctx.guild} prefix to {prefix}")
        prefixes[str(ctx.guild.id)] = prefix
        with open("prefixes.json", "w") as f:
            json.dump(prefixes, f, indent=4)
        await ctx.send(f"Changed server prefix to {prefixes[str(ctx.guild.id)]}")
        print(
            f"Prefix set command used by {ctx.author} at {now()} in server {ctx.guild}, set to {prefix}."
        )


def setup(bot):
    bot.add_cog(Management(bot))

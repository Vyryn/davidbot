import time
from collections import Counter

import requests
from discord.ext import commands
from functions import global_prefix, now, auth
from privatevars import BEARER

req_url = "https://influencesysapi.thecorporateer.com/corporateers/"
inf_threshold = 2000
spaced_needed = 18  # used to be 32


def headers():
    """For packing authorization header into api requests"""
    return {"authorization": BEARER}


def query_corporateers():
    """For fetching new data from Zollak's database"""
    r = requests.get(req_url, headers=headers())
    return r.json()


class Influence(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Events
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Cog {self.qualified_name} is ready.")

    @commands.command(
        name="infranks", description="See the distribution of influence system ranks."
    )
    @commands.guild_only()
    async def infranks(self, ctx):
        """
        Shows where you stack up in the Influence System ranks.
        """
        query = query_corporateers()

        # Rank Statistics
        ranks_list = []
        for user in query:
            ranks_list.append(user["rank"]["name"])
        ranks_counter = Counter(ranks_list)

        num_users = sum(ranks_counter.values())

        ranks_dist = {
            "Distinguished Associate": ranks_counter["Distinguished Associate"],
            "Senior Associate": ranks_counter["Senior Associate"],
            "Associate": ranks_counter["Associate"],
            "Junior Associate": ranks_counter["Junior Associate"],
            "Corporate Drone": ranks_counter["Corporate Drone"],
            "Senior Intern": ranks_counter["Senior Intern"],
            "Intern": ranks_counter["Intern"],
        }
        # print(ranks_dist)

        print(f"There are {num_users} registered users in the influence system.")
        cumulative = 0
        presentation = "Climb the Corporate Ladder by sending all your tributes every week! How do you stack up?\n"
        for name, number in ranks_dist.items():
            cumulative += number
            presentation += f"{name}s are in the top {int(cumulative / num_users * 1000) / 10}% of users.\n"
        print(presentation)
        await ctx.send(presentation)

    @commands.command(name="top", description="See the top Influence hoarders.")
    @commands.guild_only()
    async def top(self, ctx, amount_to_return=5):
        """
        Lists the top influence hoarders ;)
        """
        if amount_to_return < 0:
            amount_to_return = 5
        if amount_to_return > 20:
            amount_to_return = 20
        # Query Zollak's database for updated data
        total_inf_dict = {}
        lifetime_inf_dict = {}
        query = query_corporateers()
        # print(f'Query returned: {query}')

        for person in query:
            total_inf_dict[person["name"]] = person["totalInfluence"]
            lifetime_inf_dict[person["name"]] = person["lifetimeInfluence"]
        # print(corporateer_dict)

        presentation = (
            f"The {amount_to_return} people with the most **current** influence are:\n"
        )
        i = 0
        # Top Total Influence
        for user in sorted(
            total_inf_dict.items(), key=lambda item: item[1], reverse=True
        ):
            i += 1
            if i > amount_to_return:
                break
            presentation += f"{i}) {user[0]}\n"
        presentation += f"\nThe {amount_to_return} people with the most **lifetime** influence are:\n"
        i = 0
        # Top Lifetime Influence
        for user in sorted(
            lifetime_inf_dict.items(), key=lambda item: item[1], reverse=True
        ):
            i += 1
            if i > amount_to_return:
                break
            presentation += f"{i}) {user[0]}\n"
        presentation += "Climb to the top of the Corporate Ladder by sending all your tributes every week!\n"
        print(presentation)
        await ctx.send(presentation)

    @commands.command(name="checkinf", description="See how much Influence you have.")
    @commands.guild_only()
    async def checkinf(self, ctx):
        """
        Have the bot send you a private message with how much influence you have.
        """
        query = query_corporateers()
        people = {}
        for person in query:
            people[person["name"]] = (
                person["name"],
                person["totalInfluence"],
                person["lifetimeInfluence"],
            )
        # print(corporateer_dict)

        name = ctx.author.nick
        if name is None:
            name = ctx.author.name
        p_o_e = people.get(name, "-1")
        if p_o_e == "-1":
            await ctx.author.send(
                "Sorry, I couldn't find you in the influence system. Make sure you're registered with"
                " `~influence login` in the #bot-control-room and that your username is exactly the"
                " same as your discord nickname."
            )
            return

        await ctx.author.send(
            f"{name}, your liftime influence is {p_o_e[2]} and your current influence balance "
            f"is {p_o_e[1]}. Keep sending all your tributes to others every week to rise in the"
            f" ranks. Send to people you regularly play with or find helpful to help them rise "
            f"in the ranks as well. Remember, if you don't send all your tributes every week, "
            f"most of it will be lost."
        )


def setup(bot):
    bot.add_cog(Influence(bot))

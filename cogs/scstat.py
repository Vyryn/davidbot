import asyncio
import random
from collections import Counter

import aiohttp
import discord
import typing
from discord.ext import commands
from bs4 import BeautifulSoup as _bs
from lxml.html.clean import unicode

session = aiohttp.ClientSession()
orgstats_url = "http://scstat.com/orgs-by-growth-and-recruiting/most-growth-in-a-month"


class Scstat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def cog_unload(self):
        print(f"Closing {self.qualified_name} cog...")
        session.close()

    # Events
    # When bot is ready, print to console
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Cog {self.qualified_name} is ready.")

    @commands.command()
    async def growth(self, ctx):
        """
        Fetches some growth stats from the SCStat website.
        """
        async with session.get(orgstats_url) as response:
            soup = _bs(await response.text(), features="lxml")
            orgs_raw = soup.tbody.find_all("tr")
            orgs_cleaner = {}
            for org in orgs_raw:
                org_entry = []
                for line in org.stripped_strings:
                    try:
                        to_append = int(line)
                    except ValueError:
                        to_append = line
                    org_entry.append(to_append)
                orgs_cleaner[org_entry[1]] = org_entry
            print(orgs_cleaner)
            del orgs_cleaner["Spectrum ID"]
            corp = orgs_cleaner["CORP"]
            orgs_clean = sorted(
                orgs_cleaner.items(), key=lambda x: x[1][3], reverse=True
            )
            print(corp)
            to_send = "Top orgs by monthly new members:\n```\n"
            for org in orgs_clean[:5]:
                if org[0] == "TEST":
                    org[1][2] = "Test Squadron"
                to_send += f"{org[1][0]}) {org[1][2]} ({org[0]})  + {org[1][3]} new members in the past month.\n"
            if corp[0] > 5:
                to_send += (
                    f"{corp[0]}) {corp[2]} ({corp[1]})  + {corp[3]} new members in the past month.\n```\n"
                    f"We should be higher on the list!"
                )
            else:
                to_send += "```\nGood work, but lets see if we can get to #1!"
            await ctx.send(to_send)
            print(to_send)


def setup(bot):
    bot.add_cog(Scstat(bot))

# 3rd Joint Combat Group Discord Bot
# Codename: "JR"
#By: J. Murwin, W. Alphin

# --- basic.py --- #
# Handles the basic bot functionality commands

import discord
from discord.ext import commands
from random import randint, choice

class Basic(commands.Cog):

    def __init__(self, client):
        self.client = client

    
    # PING COMMAND #
    #just ensures bot is online and reading, returns MS ping
    @commands.command()
    async def ping(self, ctx):
        await ctx.send(f"Ping: {self.client.latency * 1000:.0f} ms")

    # FLIP COMMAND #
    #returns Heads or Tails string
    @commands.command()
    async def flip(self, ctx):
        outcomes = (
            'Heads!',
            'Tails!'
        )
        
        await ctx.send(choice(outcomes))

def setup (client):
    client.add_cog(Basic(client))
# 3rd Joint Combat Group Discord Bot
# Codename: "JR"
#By: J. Murwin, W. Alphin

# --- basic.py --- #
# Handles the basic bot functionality commands

import discord
import random
from discord.ext import commands


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
        await ctx.send(random.choice(outcomes))

    
    # ROLL COMMAND #
    @commands.command()
    async def roll(self, ctx):
        outcomes = random.randint(1,6)
        await ctx.send(outcomes)

    # 8BALL COMMAND #
    @commands.command(aliases = ['8ball'])
    async def _8ball(self, ctx, *, question):
        responses = (
                'Absolutely!',
                'Without a doubt.',
                'Most likely.',
                'Yes.',
                'Maybe.',
                'Perhaps.',
                'Nope.',
                'Very doubtful.',
                'Absolutely not.',
                'It is unlikely.',
                'Oof',
                'Yeah not gunna happen chief.',
                'Are you out of your mind?'
            )
        await ctx.send (f'Answer: {random.choice(responses)}')

def setup (client):
    client.add_cog(Basic(client))
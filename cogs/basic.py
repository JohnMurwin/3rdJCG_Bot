# 3rd Joint Combat Group Discord Bot
# Codename: "JR"
#By: J. Murwin, W. Alphin

# --- basic.py --- #
# Handles the basic bot functionality commands

import discord
import time
import random
import asyncio
import re
from bot import BotAdmin
from bot import BotCommander
from bot import BotUser
from discord.ext import commands
from discord import guild

class Basic(commands.Cog):
    
    # Client Setup
    def __init__(self, client):
        self.client = client

    # PING COMMAND #
    #just ensures bot is online and reading, returns MS ping
    @commands.command()
    @commands.has_any_role(*BotUser)
    async def ping(self, ctx):
        embed = discord.Embed(title="PING", color=0xff8100)
        embed.add_field(name="Result", value=f"{self.client.latency * 1000:.0f} ms", inline=True)

        await ctx.send(embed=embed)

    # FLIP COMMAND #
    #returns Heads or Tails string
    @commands.command()
    @commands.has_any_role(*BotUser)
    async def flip(self, ctx):
        outcomes = (
            'Heads!',
            'Tails!'
        )
        embed = discord.Embed(title="FLIP", color=0xff8100)
        embed.add_field(name="Result", value=random.choice(outcomes), inline=True)

        await ctx.send(embed=embed)
    
    # ROLL COMMAND #
    #returns 1-6 integer
    @commands.command()
    @commands.has_any_role(*BotUser)
    async def roll(self, ctx):
        outcomes = random.randint(1,6)
        embed = discord.Embed(title="ROLL", color=0xff8100)
        embed.add_field(name="Result", value=(outcomes), inline=True)

        await ctx.send(embed=embed)

    # 8BALL COMMAND #
    #returns a randomly selected response from list below
    @commands.command(aliases = ['8ball'])
    @commands.has_any_role(*BotUser)
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

    # UPTIME COMMAND #
    #returns uptime of Bot

def setup (client):
    client.add_cog(Basic(client))
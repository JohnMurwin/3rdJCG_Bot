# 3rd Joint Combat Group Discord Bot
# Codename: "JR"
#By: J. Murwin, W. Alphin

# --- basic.py --- #
# Handles the basic bot functionality commands

import discord
import time
import random
import asyncio
from discord.ext import commands


class Basic(commands.Cog):
    
    def __init__(self, client):
        self.client = client

    # PING COMMAND #
    #just ensures bot is online and reading, returns MS ping
    @commands.command()
    async def ping(self, ctx):
        embed = discord.Embed(title="PING", color=0xff8100)
        embed.add_field(name="Result", value=f"{self.client.latency * 1000:.0f} ms", inline=True)

        await ctx.send(embed=embed)

    # FLIP COMMAND #
    #returns Heads or Tails string
    @commands.command()
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
    async def roll(self, ctx):
        outcomes = random.randint(1,6)
        embed = discord.Embed(title="ROLL", color=0xff8100)
        embed.add_field(name="Result", value=(outcomes), inline=True)

        await ctx.send(embed=embed)

    # 8BALL COMMAND #
    #returns a randomly selected response from list below
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

        embed = discord.Embed(title="8-BALL", color=0xff8100)
        embed.add_field(name="Question", value=question, inline=True)
        embed.add_field(name="Answer", value=random.choice(responses), inline=False)
        
        await ctx.send (embed=embed)


    # UPTIME COMMAND #
    #returns uptime of Bot

def setup (client):
    client.add_cog(Basic(client))
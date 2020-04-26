# 3rd Joint Combat Group Discord Bot
# Codename: "JR"
#By: J. Murwin, W. Alphin

# --- dicegame.py --- #
# Handles the basic bot functionality commands

import discord
import time
import random
import asyncio
from bot import BotAdmin
from bot import BotCommander
from bot import BotUser
from discord.ext import commands
from discord import guild
from random import randint

class diceGame(commands.Cog):
    embedRed = 0xff0000
    embedGreen = 0x008000
    
    gameJoining = False
    gameOpen = False
    gameHost = None
    gameParticipants = []
    gameRolls = []
    # Dice Game#
    @commands.command()
    async def newgame(self, ctx):
        channel = ctx.message.channel
        if diceGame.gameOpen:
            await ctx.author.send("A game is already active, you must wait until the current game is complete.")
            await channel.purge(limit=1)
        else:
            diceGame.gameOpen = True
            diceGame.gameJoining = True
            author = ctx.message.author.name
            diceGame.gameHost = author
            diceGame.gameParticipants.append(author)
            await ctx.send("Starting a new game! Use !joingame to enter!")

    @commands.command()
    async def joingame(self, ctx):
        channel = ctx.message.channel
        if diceGame.gameOpen and diceGame.gameJoining:
            author = ctx.author.name
            diceGame.gameParticipants.append(author)
            await ctx.send(f"{author} has joined the game!")
        elif not diceGame.gameOpen:
            await ctx.send("A game is not currently active. Use !newgame to start one.")
        elif not diceGame.gameJoining and diceGame.gameOpen:
            await ctx.author.send("Joining is closed for the current game.")
            await channel.purge(limit=1)

    @commands.command()
    async def startgame(self, ctx):
        if not diceGame.gameOpen:
            channel = ctx.message.channel
            await ctx.author.send("There's currently no game running. Use !newgame to start a new game.")
            await channel.purge(limit=1)
        elif ctx.message.author.name != diceGame.gameHost:
            channel = ctx.message.channel
            await ctx.author.send(f"Only the host can start this game. The current game's host is {diceGame.gameHost}")
            await channel.purge(limit=1)
        else:
            diceGame.gameJoining = False
            for p in diceGame.gameParticipants:
                roll = randint(1,100)
                diceGame.gameRolls.append(roll)
            
            totalParticipants = len(diceGame.gameParticipants)
            gameParticipants = diceGame.gameParticipants
            gameRolls = diceGame.gameRolls
            
            winningRoll = max(diceGame.gameRolls)
            winningIndex = diceGame.gameRolls.index(max(diceGame.gameRolls))

            embed = discord.Embed(title=f"Winner: {diceGame.gameParticipants[winningIndex]}!", description=f"Winning Roll: {winningRoll}", color=diceGame.embedGreen)
            embed.set_footer(text = "Game over! Use !newgame to begin a new game!")
            embed.set_image(url='https://i.imgur.com/M2QQFy1.png')

            i = 0
            while i < totalParticipants:
                embed.add_field(name=f"{gameParticipants[i]}", value = f"{gameRolls[i]}")
                i += 1
          
            await ctx.send(embed=embed)

            diceGame.gameJoining = False
            diceGame.gameOpen = False
            diceGame.gameHost = None
            diceGame.gameParticipants = []
            diceGame.gameRolls = []

    @commands.command()
    async def endgame(self, ctx):
        diceGame.gameJoining = False
        diceGame.gameOpen = False
        diceGame.gameHost = None
        diceGame.gameParticipants = []
        diceGame.gameRolls = []
        await ctx.send("The current game has been closed. Start a new game with !newgame")

def setup (client):
    client.add_cog(diceGame(client))
# 3rd Joint Combat Group Discord Bot
# Codename: "JR"
#By: J. Murwin, W. Alphin

#--CONFIG--
token = "NTg5OTk3MTE3MTIxMjMyOTM3.XoyVzw.N5IV-mpG-edUdDr9VbTwDMhVClM" 
prefix = "!"

#Discord Setup
import discord
import os
from discord.ext import commands

#Command Prefix Setup
client = commands.Bot(command_prefix = prefix)

# LOAD COGS #
@client.command()
async def load(ctx, extension):
    client.load_extension(f'cogs.{extension}')

# UNLOAD COGS #
@client.command()
async def unload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')


# AUTO-LOAD COGS#
for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}') # load the extension but splice off the .py


# RUN MOFO #
client.run(token)
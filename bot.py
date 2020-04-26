# 3rd Joint Combat Group Discord Bot
# Codename: "JR"
#By: J. Murwin, W. Alphin

# --- bot.py --- #
# Handles the loading of the cogs & initilization functions

#Discord Setup
import discord
import os
import json
from discord.ext import commands

#Token & Prefix Retrieval from JSON
token = json.loads(open("config.json").read())["DISCORD_TOKEN"]
prefix = json.loads(open("config.json").read())["PREFIX"]

#User Retrieval from JSON
BotAdmin = json.loads(open("config.json").read())["BOT_ADMIN"]
BotCommander = json.loads(open("config.json").read())["BOT_COMMANDER"]
BotUser = json.loads(open("config.json").read())["BOT_USER"]

#Command Prefix Setup
client = commands.Bot(command_prefix = prefix)

# READY #
@client.event
async def on_ready():
    print ('Jr is Online')
    #set bot status
    await client.change_presence(status=discord.Status.online, activity=discord.Game('!help'))


# CLEAR ALL MESSAGES COMMAND # 
@client.command(pass_context=True)
@commands.has_any_role(*BotAdmin)
async def clearall(ctx, amount=10):
    channel = ctx.message.channel

    await channel.purge(limit=int(amount))

# CLEAR BOT MESSAGES COMMAND #
@client.command(pass_context=True)
@commands.has_any_role(*BotAdmin, *BotCommander)
async def clearbot(ctx, amount=10):
    def is_me(m):
        return m.author == client.user

    channel = ctx.message.channel

    await channel.purge(limit=int(amount), check=is_me)

# LOAD COGS #
@client.command()
@commands.has_any_role(*BotAdmin)
async def load(ctx, extension):
    client.load_extension(f'cogs.{extension}')
    await ctx.send ('Extension Loaded')


# UNLOAD COGS #
@client.command()
@commands.has_any_role(*BotAdmin)
async def unload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')
    await ctx.send ('Extension UnLoaded')


# RELOAD COG #
@client.command()
@commands.has_any_role(*BotAdmin)
async def reload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')
    client.load_extension(f'cogs.{extension}')
    await ctx.send ('Extension ReLoaded')


# AUTO-LOAD COGS#
for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}') # load the extension but splice off the .py

# RUN MOFO #
client.run(token)
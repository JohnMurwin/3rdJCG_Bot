# 3rd Joint Combat Group Discord Bot
# Codename: "JR"
#By: J. Murwin, W. Alphin

# --- bot.py --- #
# Handles the loading of the cogs & initilization functions

#Discord Setup
import discord
import os
import json
import re
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

# NEW MEMBER MESSAGE #
#messages new members on connection
@client.event
async def on_member_join(member):
#channel = client.get_channel(697607359765282817)
    mentionMember = member.mention
    welcomeMessage = "__**Welcome to the 3rd Joint Combat Group Discord!**__\r \r"\
        "Start off by reading over everything in the **#rules** channel and updating your discord nickname to an RP name.\r" \
        "Your RP name should use the following format **[J. Doe]**. You will recieve the Recruit role automatically once you have done so.\r"\
        "If you're here for ARMA, begin reading over the information in the **#getting-started** and **#recruit-info** channels.\r"\
        "When you're ready to begin your orentation or if you have any questions, **@Recruiter** in the **#recruit-comms** channel.\r"\
        "If you're joining as a friend of a current member and not for ARMA, have your friend coordinate with us to get you the appropriate discord permissions.\r\r" \
        "__**Thanks for joining, we look forward to gaming with you!**__"
            
    await member.send(welcomeMessage)
#await channel.send(f"Welcome {mentionMember}!")

# NEW MEMBER ROLE #
#assigns new members the recruit role after they have changed their discord name

@client.event
async def on_member_update(before, after):
    if after.nick != None:

        nickNameAfter = after.nick
        nickNameBefore = before.nick
        #nickname formats allowed W.Alphin and W. Alphin
        nickPattern1 = "((?:[A-Z][-. ]+)+) ([- A-Za-z]+(?:, \w+)?)"
        nickPattern2 = "((?:[A-Z][-. ]+)+)([- A-Za-z]+(?:, \w+)?)"

        role = discord.utils.get(after.guild.roles, name='Recruit')
        memberRoles = [role.name for role in after.roles]

        if nickNameBefore != nickNameAfter:
            if "Recruit" not in memberRoles:
                if ("Member" or "MIA" or "Unit Friend" or "Phase 1" or "Phase 2" or "Phase 3") in memberRoles:
                    pass
                else:
                    if re.match(nickPattern1, nickNameAfter) or re.match(nickPattern2, nickNameAfter):
                        await after.add_roles(role)

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
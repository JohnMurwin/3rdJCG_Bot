# 3rd Joint Combat Group Discord Bot
# Codename: "JR"

#J. Murwin, W. Alphin

import discord
from discord.ext import commands

#Command Prefix Setup
client = commands.Bot(command_prefix = '!')

# EVENTS #
@client.event
async def on_ready():
    print ('Jr is Online')


#RUN MOFO #
client.run('NTg5OTk3MTE3MTIxMjMyOTM3.XoyVzw.N5IV-mpG-edUdDr9VbTwDMhVClM')
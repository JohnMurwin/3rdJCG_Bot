# 3rd Joint Combat Group Discord Bot
# Codename: "JR"
#By: J. Murwin, W. Alphin

# --- missions.py --- #
# Handles mission related commands and functionality

import discord
import json
import time
import random
import asyncio
import datetime
import re
import mysql.connector
from discord.ext import commands
from datetime import timedelta
from datetime import datetime
from discord.utils import get

#pull DB connection from secure file
dbhost = json.loads(open("config.json").read())["DBHOST"]
dbuser = json.loads(open("config.json").read())["DBUSER"]
dbpw = json.loads(open("config.json").read())["DBPW"]
db = json.loads(open("config.json").read())["DB"]
missionsPath = json.loads(open("config.json").read())["MISSIONPATH"]

def init_db():
    return mysql.connector.connect(
        host= dbhost,
        user= dbuser,
        passwd= dbpw,
        database= db
        )

# embed colors
embedRed = 0xff0000
embedGreen = 0x008000

 # roles used for alert and role sign up commands
roleIndex = ["Armor","Artillery","Engineer","FixedWing","Medic","Recon","Rotary","RTO","RP"]

# MISSIONS TABLE INDEX #
# id, name, date, time ,author, channelid, mentioned

class missions(commands.Cog):

    def __init__(self, client):
        self.client = client

    # New Mission #
    @commands.command(aliases=['nm'])
    async def newMission(self, ctx, missionName=None, missionDate=None, missionMaker="none", missionTime="19:00", createChannel=True):
        #before anything else, make sure the required parameters are provided, if not, send the user a message
        if missionName == None or missionDate == None:
            embed = discord.Embed(title="Syntax Error", description="The mission name and date are required.", color=embedRed)
            embed.add_field(name='Example:', value = "!nm \"Power Overwhelming\" 01/01/20", inline=False)
            embed.set_image(url='https://i.imgur.com/M2QQFy1.png')
            await ctx.send(embed = embed)
            return
        
        #connect to the db
        mydb = init_db()

        attachments = ctx.message.attachments
        #check missions table for a mission reserved on the provided date, if none exist, log the new mission
        mycursor = mydb.cursor()
        mycursor.execute("SELECT * FROM missions WHERE date = %s", (missionDate,))
        count = 0
        missionQuery = [row[1:5] for row in mycursor.fetchall()]

        for i in missionQuery:
            count += 1

        #verify input and log the mission to file
        if count == 0:

            mycursor = mydb.cursor()
            mycursor.execute("SELECT * FROM missions WHERE name = %s", (missionName,))
            nameQuery = mycursor.fetchall()
            nCount = 0
            
            for i in nameQuery:
                nCount += 1
            
            if nCount > 0:
                embed = discord.Embed(title="Mission Name Already Used", color=embedRed)
                embed.add_field(name = "ERROR:", value = "A unique mission name is required.", inline=False)
                await ctx.send(embed=embed)
                return

            #verify date format
            try: 
                datetime.strptime(missionDate, '%m/%d/%y')
                invalidDate = False
            except:
                invalidDate = True

            #verify time format using regex
            #using regex because I couldn't figure this out using datetime - code copied from stackoverflow
            time_re = re.compile(r'^(([01]\d|2[0-3]):([0-5]\d)|24:00)$')
            def valid_time_format(s):
                return bool(time_re.match(s))

            if valid_time_format(missionTime):
                invalidTime = False
            else:
                invalidTime = True

            if  not invalidDate and not invalidTime:
                #create the mission channel for the author to post the dossier
                if createChannel:
                    category = get(ctx.guild.categories, name="OPERATIONS")
                    channel = await ctx.guild.create_text_channel(missionName,overwrites=None,category = category)
                    channelID = channel.id
                    
                    if missionMaker == "none":
                        missionMaker = ctx.author.nick

                    introMessage = f"__**{missionName}**__\rThis mission is scheduled for: **{missionDate}** @ **{missionTime}**\rAuthor: **{missionMaker}**"
                    await channel.send(introMessage)
                else:
                    channelID = 0

                mycursor = mydb.cursor()
                sql = "INSERT INTO missions (name, date, time, author, channelid) VALUES (%s, %s, %s, %s, %s)"
                values = (missionName, missionDate, missionTime, missionMaker, channelID)
                mycursor.execute(sql, values)
                mydb.commit()

                embed = discord.Embed(title="Reserving Mission: {}".format(missionName), color=embedGreen)
                embed.add_field(name='Name', value = missionName, inline=False)
                embed.add_field(name="Date", value = missionDate, inline=False)
                embed.add_field(name="Time", value = missionTime, inline=False)                    
                embed.add_field(name="Author", value = missionMaker, inline=False)
                embed.set_image(url='https://i.imgur.com/M2QQFy1.png')
                

                if attachments !=[]:
                    attachment = ctx.message.attachments[0]
                    fileName = attachment.filename
                    if fileName[-3:] != "pbo":
                        await ctx.author.send("Only a .pbo file may be used when uploading mission files.")
                    else:
                        try:
                            await attachment.save(f"{missionsPath}{fileName}")
                            embed.set_footer(text=f"Mission file: {fileName} has been uploaded")
                        except:
                            await ctx.author.send("An error occurred while uplading your mission file. The file may be in use")
                            embed.set_footer(text="No mission file attached. Use !upload to upload your mission file to the server.")
                else:
                    embed.set_footer(text="No mission file attached. Use !upload to upload your mission file to the server.")

                await ctx.send(embed=embed)

            elif invalidDate:
                embed = discord.Embed(title="Invalid Date Format", color=embedRed)
                embed.add_field(name = "ERROR:", value = "Use MM/DD/YY i.e 1/1/20", inline=False)
                await ctx.send(embed=embed)
            else:
                embed = discord.Embed(title="Invalid Time Format", color=embedRed)
                embed.add_field(name = "ERROR:", value = "Use HH:MM i.e 24:00", inline=False)
                await ctx.send(embed=embed)

        elif count > 0: #create the embed response
            embed = discord.Embed(title="Date already Claimed by: {}".format(missionQuery[0][0]), color=embedRed)
            embed.add_field(name="Name", value = missionQuery[0][0], inline=False)
            embed.add_field(name="Date", value = missionQuery[0][1], inline=False)
            embed.add_field(name="Time", value = missionQuery[0][2], inline=False)          
            embed.add_field(name="Author", value = missionQuery[0][3], inline=False)
            embed.set_image(url='https://i.imgur.com/M2QQFy1.png')
            await ctx.send(embed=embed)
        #close the db connection
        mydb.close()
    # Cancel Mission #

    @commands.command(aliases = ['cm'])
    async def cancelMission(self, ctx, missionName=None):
        #before anything else, make sure the required parameters are provided, if not, send the user a message
        if missionName == None:
            embed = discord.Embed(title="Syntax Error", description="The mission name is required.", color=embedRed)
            embed.add_field(name='Example:', value = "!cm \"Power Overwhelming\"", inline=False)
            embed.set_image(url='https://i.imgur.com/M2QQFy1.png')
            await ctx.send(embed = embed)
            return
        #connect to the db
        mydb = init_db()

        #wrote this late and not entirely sure why it works compared to previous methods but I'm leaving it because it works
        mycursor = mydb.cursor()
        mycursor.execute("SELECT * FROM missions WHERE name = %s", (missionName,))
        count = 0
        result = [row[1:7] for row in mycursor.fetchall()]
        for i in result:
            count += 1
        if count != 0:
            channelID = int(result[0][4])
            
            embed = discord.Embed(title="Mission: {} has been deleted".format(missionName), color=embedGreen)
            embed.set_image(url='https://i.imgur.com/M2QQFy1.png')
            await ctx.send(embed=embed)
            if channelID != 0:
                channel = get(ctx.guild.channels, id=channelID)
                await discord.TextChannel.delete(channel)

            mycursor = mydb.cursor()
            mycursor.execute("DELETE FROM missions WHERE name = %s", (missionName,)) 
            mydb.commit()    

        else:
            embed = discord.Embed(title="Mission: {} was not found".format(missionName), description = "Make sure the name of the mission is correct and try again", color=embedRed)
            embed.set_image(url='https://i.imgur.com/M2QQFy1.png')
            await ctx.send(embed=embed)

        mydb.close()
    # List Missions #

    @commands.command(aliases = ['lm'])
    async def listMission(self, ctx, field=None, fieldValue=None):
        #connect to the db
        mydb = init_db()

        missionDate, missionName, missionMaker, invalidDate = None, None, None, None
        #setup vars based on parameters input
        #to deal with case sensitivity, I'm going to create a list of options for them to check instead of using a bunch of or operators
        dateParameters = ['Date','date']
        nameParameters = ['Name','name']
        authorParameters = ['Author','author']

        today = datetime.now().date()
        daysAhead = today + timedelta(days=7)
        todayStr = today.strftime('%m/%d/%y')
        daysAheadStr = daysAhead.strftime('%m/%d/%y')


        if field in dateParameters:
            missionDate = fieldValue
        elif field in nameParameters:
            missionName = fieldValue
        elif field in authorParameters:
            missionMaker = fieldValue
        elif field != None and fieldValue == None:
            embed = discord.Embed(title="ERROR:", description = "Search type was provided without a value.", color=embedRed)
            embed.add_field(name="Example:", value= "!lm date 4/20/20", inline=True)
            embed.set_image(url='https://i.imgur.com/M2QQFy1.png')
            await ctx.send(embed=embed)
            return

        #validate the date format
        if missionDate !=None:
            try: 
                datetime.strptime(missionDate, '%m/%d/%y')
                invalidDate = False
            except:
                invalidDate = True

        if invalidDate:
            embed = discord.Embed(title="Invalid Date Format", color=embedRed)
            embed.add_field(name = "ERROR:", value = "Use MM/DD/YY i.e 1/1/20", inline=False)
            embed.set_image(url='https://i.imgur.com/M2QQFy1.png')
            await ctx.send(embed=embed)
        else:
            #if no parameters are supplied, just listed the missions in the file for the next 7 days
            if missionDate == None and missionMaker == None and missionName == None:
                mycursor = mydb.cursor()
                sql = "SELECT * FROM missions ORDER BY date"
                mycursor.execute(sql)
                totalCount = 0
                count = 0
                result = [row[1:5] for row in mycursor.fetchall()]

                for i in result:
                    totalCount += 1
                for x in range(0,totalCount):
                    if datetime.strptime(result[x][1], '%m/%d/%y') >= datetime.strptime(todayStr, '%m/%d/%y'):
                        embed = discord.Embed(title="Mission: {}".format(result[x][0]), color=embedGreen)
                        embed.add_field(name="Name", value = result[x][0], inline=False)
                        embed.add_field(name="Date", value = result[x][1], inline=False)
                        embed.add_field(name="Time", value = result[x][2], inline=False)                        
                        embed.add_field(name="Author", value = result[x][3], inline=False)
                        embed.set_image(url='https://i.imgur.com/M2QQFy1.png')
                        await ctx.send(embed=embed)
                        count += 1

            #else if misison date is supplied, list the mission with the cooresponding date
            elif missionDate != None:

                mycursor = mydb.cursor()
                mycursor.execute("SELECT * FROM missions WHERE date=%s", (missionDate,))
                count = 0
                result = [row[1:5] for row in mycursor.fetchall()]

                for i in result:
                    count += 1
                for x in range(0,count):
                    if result[x][1] >= todayStr:
                        embed = discord.Embed(title="Mission: {}".format(result[x][0]), color=embedGreen)
                        embed.add_field(name="Name", value = result[x][0], inline=False)
                        embed.add_field(name="Date", value = result[x][1], inline=False)
                        embed.add_field(name="Time", value = result[x][2], inline=False)                  
                        embed.add_field(name="Author", value = result[x][3], inline=False)
                        embed.set_image(url='https://i.imgur.com/M2QQFy1.png')
                        await ctx.send(embed=embed)

            elif missionName !=None:

                mycursor = mydb.cursor()
                mycursor.execute("SELECT * FROM missions WHERE name = %s", (missionName,))
                count = 0
                result = [row[1:5] for row in mycursor.fetchall()]

                for i in result:
                    count += 1
                for x in range(0,count):
                    if result[x][1] >= todayStr:
                        embed = discord.Embed(title="Mission: {}".format(result[x][0]), color=embedGreen)
                        embed.add_field(name="Name", value = result[x][0], inline=False)
                        embed.add_field(name="Date", value = result[x][1], inline=False)
                        embed.add_field(name="Time", value = result[x][2], inline=False)                        
                        embed.add_field(name="Author", value = result[x][3], inline=False)
                        embed.set_image(url='https://i.imgur.com/M2QQFy1.png')
                        await ctx.send(embed=embed)

            elif missionMaker !=None:
                
                mycursor = mydb.cursor()
                mycursor.execute("SELECT * FROM missions WHERE author = %s", (missionMaker,))
                count = 0
                result = [row[1:5] for row in mycursor.fetchall()]

                # reference the table index at the top of the file for referenced columns below
                for i in result:
                    count += 1
                for x in range(0,count):
                    if result[x][1] >= todayStr:
                        embed = discord.Embed(title="Mission: {}".format(result[x][0]), color=embedGreen)
                        embed.add_field(name="Name", value = result[x][0], inline=False)
                        embed.add_field(name="Date", value = result[x][1], inline=False)
                        embed.add_field(name="Time", value = result[x][2], inline=False)                       
                        embed.add_field(name="Author", value = result[x][3], inline=False)
                        embed.set_image(url='https://i.imgur.com/M2QQFy1.png')
                        await ctx.send(embed=embed) 

            if count == 0:
                embed = discord.Embed(title="No missions were found", description = "Check your spelling, try a different pramemter or no future missions have been scheduled at this time.", color=embedRed)
                embed.set_image(url='https://i.imgur.com/M2QQFy1.png')
                await ctx.send(embed=embed)
        mydb.close()
    
    # Mission Notify #
    @commands.command(aliases = ['yell'])
    async def alert(self, ctx, test=False):
        #connect to the db
        mydb = init_db()

        messageAuthor = ctx.author.nick
        channelID = ctx.channel.id
        channel = ctx.message.channel
        mycursor = mydb.cursor()
        mycursor.execute("SELECT author, mentioned FROM missions WHERE channelid = %s", (channelID,))
        result = [row[0:2] for row in mycursor.fetchall()]
        missionAuthor = result[0][0]
        mentioned = result[0][1]
        mentioned = 0

        if missionAuthor != messageAuthor:
            embed = discord.Embed(title="Notify Failure", description="You must be the mission author to notify everyone", color=embedRed)
            embed.set_image(url='https://i.imgur.com/M2QQFy1.png')
            await ctx.author.send(embed=embed)
            await channel.purge(limit=1)
        elif mentioned == 1:
            embed = discord.Embed(title="Notify Failure", description="Notification alredy sent", color=embedRed)
            embed.add_field(name="NOTE:", value = "If you need another ping, contact an Advocate or Council member", inline=False)
            embed.set_image(url='https://i.imgur.com/M2QQFy1.png')
            await ctx.author.send(embed=embed)
            await channel.purge(limit=1)
        else:
            await channel.purge(limit=1)
            mycursor = mydb.cursor()
            mycursor.execute("UPDATE missions SET mentioned = '1' WHERE channelid = %s", (channelID,))
            mydb.commit()

            if test == False:
                await ctx.send("@everyone")   #store message for reactions posting
            else:
                await ctx.send(ctx.author.mention)

            # build the role sign up embed
            embed = discord.Embed(title="Role Sign-Up", color=embedGreen)
            embed.add_field(name="__**Attending**__ \U0001F44D", value='0', inline=True)
            embed.add_field(name="__**Late**__ \U000023F2", value='0', inline=False)
            embed.set_footer(text="Order: First to last per role | Position is not saved if removed.")
            embed.add_field(name='\u200b', value='\u200b', inline=False)

            emojiList = self.client.emojis
            roleEmojiList = ['\U0001F44D','\U000023F2']
            for role in roleIndex:
                for emoji in emojiList:
                    if emoji.name == role:
                        roleEmojiList.append(self.client.get_emoji(emoji.id))
                        embed.add_field(name=f"{emoji} {emoji.name}",value='\u200b') 

            embed.set_image(url='https://i.imgur.com/M2QQFy1.png')
            msg = await ctx.send(embed=embed)

            for emoji in roleEmojiList: #add reaction to post
                await msg.add_reaction(emoji)

        mydb.close()         

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
                
        guild = self.client.get_guild(payload.guild_id)
        channel = self.client.get_channel(payload.channel_id)
        userNick = guild.get_member(payload.user_id).nick

        # get the channel and message that is being reacted to
        reactChannel = self.client.get_channel(payload.channel_id)
        reactMessage = payload.message_id
        msg = await reactChannel.fetch_message(reactMessage)

        # if the message doesn't have an embed, do nothing, else
        if msg.embeds != []:
            msgEmbed = msg.embeds[0]
            embedTitle = msgEmbed.title
            reactedEmoji = payload.emoji
            reactedEmojiName = reactedEmoji.name
            embedFields = set()

            # check the title of the embed to make sure it's for role assignment
            if embedTitle == "Role Sign-Up":
                if userNick != None:
                    if reactedEmojiName in roleIndex or reactedEmojiName in ['\U0001F44D','\U000023F2']:

                        msgReactions = msg.reactions
                        attendingReactionCount = msgReactions[0].count - 1
                        lateReactionCount = msgReactions[1].count - 1
                        for field in msgEmbed.fields:

                            if field.name == f"{reactedEmoji} {reactedEmojiName}":
                                if userNick in field.value:
                                    return
                                else:
                                    if '\u200b' in field.value:
                                        newFieldValue = userNick
                                        msgEmbed.set_field_at(roleIndex.index(reactedEmojiName)+3, name=field.name, value=newFieldValue, inline=True)
                                    else:
                                        newFieldValue = field.value + f"\r {userNick}"
                                        msgEmbed.set_field_at(roleIndex.index(reactedEmojiName)+3, name=field.name, value=newFieldValue, inline=True)

                            # update attending/late numbers
                            elif reactedEmojiName == '\U0001F44D':
                                msgEmbed.set_field_at(0, name="__**Attending**__ \U0001F44D", value=str(attendingReactionCount), inline=True)
                            elif reactedEmojiName == '\U000023F2':
                                msgEmbed.set_field_at(1, name="__**Late**__ \U000023F2", value=str(lateReactionCount), inline=False)
                        await msg.edit(embed=msgEmbed)
                        await asyncio.sleep(2)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        
        guild = self.client.get_guild(payload.guild_id)
        channel = self.client.get_channel(payload.channel_id)
        userNick = guild.get_member(payload.user_id).nick

        # get the channel and message that is being reacted to
        reactChannel = self.client.get_channel(payload.channel_id)
        reactMessage = payload.message_id
        msg = await reactChannel.fetch_message(reactMessage)

        # if the message doesn't have an embed, do nothing, else
        if msg.embeds != []:
            msgEmbed = msg.embeds[0]
            
            embedTitle = msgEmbed.title
            reactedEmoji = payload.emoji
            reactedEmojiName = reactedEmoji.name
            embedFields = set()

            # check the title of the embed to make sure it's for role assignment
            if embedTitle == "Role Sign-Up":
                if userNick != None:
                    if reactedEmojiName in roleIndex or reactedEmojiName in ['\U0001F44D','\U000023F2']:

                        msgReactions = msg.reactions
                        attendingReactionCount = msgReactions[0].count - 1
                        lateReactionCount = msgReactions[1].count - 1
                        for field in msgEmbed.fields:

                            if field.name == f"{reactedEmoji} {reactedEmojiName}":
                                if field.value == userNick:
                                    newFieldValue = field.value.replace(userNick,'\u200b')
                                else:
                                    newFieldValue = field.value.replace(userNick,"")
                                #await channel.send(f"ValueN: {newFieldValue}")
                                msgEmbed.set_field_at(roleIndex.index(reactedEmojiName)+3, name=field.name, value=newFieldValue, inline=True)

                            # update attending/late numbers
                            elif reactedEmojiName == '\U0001F44D':
                                msgEmbed.set_field_at(0, name="__**Attending**__ \U0001F44D", value=str(attendingReactionCount), inline=True)
                            elif reactedEmojiName == '\U000023F2':
                                msgEmbed.set_field_at(1, name="__**Late**__ \U000023F2", value=str(lateReactionCount), inline=False)
                        
                        await msg.edit(embed=msgEmbed)
                        await asyncio.sleep(2)
    @commands.command(aliases = ['upload'])
    async def uploadMission(self, ctx):
        attachments = ctx.message.attachments

        #allows user to upload a .pbo file to the provided path
        if attachments !=[]:
            attachment = ctx.message.attachments[0]
            fileName = attachment.filename
            if fileName[-3:] != "pbo":
                embed = discord.Embed(title="Upload Failure", description="Only a .pbo file may be used when uploading mission files", color=embedRed)
                await ctx.send(embed=embed)
            else:
                try:
                    await attachment.save(f"{missionsPath}{fileName}")
                    embed = discord.Embed(title="Upload Success", description="Your mission file has been uploaded", color=embedGreen)
                    await ctx.send(embed=embed)
                except:
                    embed = discord.Embed(title="Upload Failure", description="An error occurred while uplading your mission file. The file may be in use", color=embedGreen)
                    await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="Upload Failure", description="You didn't attach a file to upload.. what did you think would happen?", color=embedRed)
            embed.set_footer(text="I mean seriously.. what did you think would happen?")
            await ctx.send(embed=embed)


def setup (client):
    client.add_cog(missions(client))
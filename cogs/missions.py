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

#pull DB connection from secure file
dbhost = json.loads(open("config.json").read())["DBHOST"]
dbuser = json.loads(open("config.json").read())["DBUSER"]
dbpw = json.loads(open("config.json").read())["DBPW"]
db = json.loads(open("config.json").read())["DB"]
missionsPath = json.loads(open("config.json").read())["MISSIONPATH"]

mydb = mysql.connector.connect(
            host= dbhost,
            user= dbuser,
            passwd= dbpw,
            database= db
            )

embedRed = 0xff0000
embedGreen = 0x008000

# MISSIONS TABLE INDEX #
# id, name, date, time ,author, channelid, mentioned

class missions(commands.Cog):

    def __init__(self, client):
        self.client = client

    # New Mission #
    @commands.command(aliases=['nm'])
    async def newMission(self, ctx, missionName, missionDate, missionMaker="none", missionTime="19:00", createChannel=True):
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
                    category = discord.utils.get(ctx.guild.categories, name="OPERATIONS")
                    channel = await ctx.guild.create_text_channel(missionName,overwrites=None,category = category)
                    channelID = channel.id
                else:
                    channelID = 0

                if missionMaker == "none":
                    missionMaker = ctx.author.nick

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

    # Cancel Mission #

    @commands.command(aliases = ['cm'])
    async def cancelMission(self, ctx, missionName):
        
        #wrote this late and not entirely sure why it works compared to previous methods but I'm leaving it because it works
        mycursor = mydb.cursor()
        mycursor.execute("SELECT * FROM missions WHERE name = %s", (missionName,))
        count = 0
        result = [row[1:7] for row in mycursor.fetchall()]
        for i in result:
            count += 1
        if count != 0:
            channelID = int(result[0][4])
            
            embed = discord.Embed(title="Mission: {} has been deleted".format(missionName), description = "Mission go bye bye", color=embedGreen)
            embed.set_image(url='https://i.imgur.com/M2QQFy1.png')
            await ctx.send(embed=embed)
            if channelID != 0:
                channel = discord.utils.get(ctx.guild.channels, id=channelID)
                await discord.TextChannel.delete(channel)

            mycursor = mydb.cursor()
            mycursor.execute("DELETE FROM missions WHERE name = %s", (missionName,)) 
            mydb.commit()    

        else:
            embed = discord.Embed(title="Mission: {} was not found".format(missionName), description = "Either you spell like Friedel or it ain't there", color=embedRed)
            embed.set_image(url='https://i.imgur.com/M2QQFy1.png')
            await ctx.send(embed=embed)

    # List Missions #

    @commands.command(aliases = ['lm'])
    async def listMission(self, ctx, field=None, fieldValue=None):

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
                count = 0
                result = [row[1:5] for row in mycursor.fetchall()]

                for i in result:
                    count += 1
                for x in range(0,count):
                    if datetime.strptime(result[x][1], '%m/%d/%y') >= datetime.strptime(todayStr, '%m/%d/%y'):
                        embed = discord.Embed(title="Mission: {}".format(result[x][0]), color=embedGreen)
                        embed.add_field(name="Name", value = result[x][0], inline=False)
                        embed.add_field(name="Date", value = result[x][1], inline=False)
                        embed.add_field(name="Time", value = result[x][2], inline=False)                        
                        embed.add_field(name="Author", value = result[x][3], inline=False)
                        embed.set_image(url='https://i.imgur.com/M2QQFy1.png')
                        await ctx.send(embed=embed)

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

    # Mission Notify #

    @commands.command(aliases = ['notify'])
    async def yell(self, ctx):
        messageAuthor = ctx.author.nick
        channelID = ctx.channel.id
        channel = ctx.message.channel
        mycursor = mydb.cursor()
        mycursor.execute("SELECT author, mentioned FROM missions WHERE channelid = %s", (channelID,))
        result = [row[0:2] for row in mycursor.fetchall()]
        missionAuthor = result[0][0]
        mentioned = result[0][1]

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
            await ctx.send("@everyone")


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
# 3rd Joint Combat Group Discord Bot
# Codename: "JR"
#By: J. Murwin, W. Alphin

# --- missions.py --- #
# Handles mission related commands and functionality

import discord
import time
import random
import asyncio
import csv
import datetime
import re
from discord.ext import commands
from datetime import timedelta

missionsFile = '.\data\missions.csv'

class missions(commands.Cog):

    def __init__(self, client):
        self.client = client

    
    # Reserve Mission #
    @commands.command(aliases=['rm'])
    async def reservemission(self, ctx, missionName, missionDate, missionTime, missionMaker, reconTime=None):

        #check missions file for an existing mission, if it doesn't exist, log/reserve it
        dateReserved = False
        with open(missionsFile, 'rt') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for row in reader:
                if missionDate == row[1]:
                    dateReserved = True
                    rMissionName = row[0]
                    rMissionDate = row[1]
                    rMissionTime = row[2]
                    rMissionMaker = row[3]
                    rReconTime = row[4]
                else:
                    dateReserved = False

        #log the mission to file
        if not dateReserved:

            #verify date format
            try: 
                datetime.datetime.strptime(missionDate, '%m/%d/%y')
                invalidDate = False
            except:
                invalidDate = True

            #verify time format using regex
            #using regex because I couldn't figure this out using datetime - code copied from stackoverflow
            time_re = re.compile(r'^(([01]\d|2[0-3]):([0-5]\d)|24:00)$')
            def valid_time_format(s):
                return bool(time_re.match(s))

            if reconTime !=None:
                if valid_time_format(missionTime) and valid_time_format(reconTime):
                    invalidTime = False
                else:
                    invalidTime = True
            elif valid_time_format(missionTime):
                    invalidTime = False
            else:
                invalidTime = True

            if  not invalidDate and not invalidTime:
                #create the mission channel for the author to post the dossier
                category = discord.utils.get(ctx.guild.categories, name="Operations")
                channel = await ctx.guild.create_text_channel(missionName,overwrites=None,category = category)
                channelID = channel.id
                with open(missionsFile, 'a', newline='') as csvfile:
                    writer = csv.writer(csvfile, delimiter=',')
                    writer.writerow([missionName, missionDate, missionTime, missionMaker, reconTime,channelID])
                    embed = discord.Embed(title="Reserving Mission: {}".format(missionName), color=0x008000)
                    embed.add_field(name='Name', value = missionName, inline=False)
                    embed.add_field(name="Date", value = missionDate, inline=False)
                    embed.add_field(name="Time", value = missionTime, inline=False)
                    if reconTime != None:
                        embed.add_field(name="Recon", value = reconTime, inline=False)
                    
                    embed.add_field(name="Author", value = missionMaker, inline=False)
                    embed.set_image(url='https://i.imgur.com/M2QQFy1.png')
                    await ctx.send(embed=embed)


            elif invalidDate:
                embed = discord.Embed(title="Invalid Date Format", color=0xff0000)
                embed.add_field(name = "ERROR:", value = "Use MM/DD/YY i.e 1/1/20", inline=False)
                await ctx.send(embed=embed)
            else:
                embed = discord.Embed(title="Invalid Time Format", color=0xff0000)
                embed.add_field(name = "ERROR:", value = "Use HH:MM i.e 24:00", inline=False)
                await ctx.send(embed=embed)

        elif dateReserved: #create the embed response
            embed = discord.Embed(title="Date already Claimed by: {}".format(rMissionName), color=0xff0000)
            embed.add_field(name="Name", value = rMissionName, inline=False)
            embed.add_field(name="Date", value = rMissionDate, inline=False)
            embed.add_field(name="Time", value = rMissionTime, inline=False)
            if rReconTime != '':
               embed.add_field(name="Recon", value = rReconTime, inline=False)
            
            embed.add_field(name="Author", value = rMissionMaker, inline=False)
            embed.set_image(url='https://i.imgur.com/M2QQFy1.png')
            await ctx.send(embed=embed)

    # Cancel Mission #

    @commands.command(aliases = ['cm'])
    async def cancelMission(self, ctx, missionName):
        missionInList = False
        #wrote this late and not entirely sure why it works compared to previous methods but I'm leaving it because it works
        with open(missionsFile, "r") as f:
            data = list(csv.reader(f))


        with open(missionsFile, "w", newline='') as f:
            writer = csv.writer(f)
            for row in data:
                if row[0] != missionName:
                    writer.writerow(row)
                    missionInList = False
                else:
                    missionInList = True
                    channelID = int(row[5])

        if missionInList:
            embed = discord.Embed(title="Mission: {} has been deleted".format(missionName), description = "Mission go bye bye", color=0xff0000)
            embed.set_image(url='https://i.imgur.com/M2QQFy1.png')
            await ctx.send(embed=embed)
            channel = discord.utils.get(ctx.guild.channels, id=channelID)
            await discord.TextChannel.delete(channel)

        else:
            embed = discord.Embed(title="Mission: {} was not found".format(missionName), description = "Either you spell like Friedel or it ain't there", color=0xff0000)
            embed.set_image(url='https://i.imgur.com/M2QQFy1.png')
            await ctx.send(embed=embed)

    # List Missions #

    @commands.command(aliases = ['lm'])
    async def listMission(self, ctx, field=None, fieldValue=None):
        missionFound = None
        missionDate = None
        missionName = None
        missionMaker = None
        invalidDate = None
        #today is actually the day prior to make sure missions reserved on the day of the command are picked up
        today = datetime.datetime.now() - timedelta(days=1)
        daysAhead = today + timedelta(days=7)

        #setup vars based on parameters input
        #to deal with case sensitivity, I'm going to create a list of options for them to check instead of using a bunch of or operators
        dateParameters = ['Date','date']
        nameParameters = ['Name','name']
        authorParameters = ['Author','author']

        if field in dateParameters:
            missionDate = fieldValue
        elif field in nameParameters:
            missionName = fieldValue
        elif field in authorParameters:
            missionMaker = fieldValue
        elif field != None and fieldValue == None:
            embed = discord.Embed(title="ERROR:", description = "Search type was provided without a value.", color=0xff0000)
            embed.add_field(name="Example:", value= "!lm date 4/20/20", inline=True)
            embed.set_image(url='https://i.imgur.com/M2QQFy1.png')
            await ctx.send(embed=embed)
            return



        #validate the date format
        if missionDate !=None:
            try: 
                datetime.datetime.strptime(missionDate, '%m/%d/%y')
                invalidDate = False
            except:
                invalidDate = True

        if invalidDate:
            embed = discord.Embed(title="Invalid Date Format", color=0xff0000)
            embed.add_field(name = "ERROR:", value = "Use MM/DD/YY i.e 1/1/20", inline=False)
            embed.set_image(url='https://i.imgur.com/M2QQFy1.png')
            await ctx.send(embed=embed)
        else:
            #if no parameters are supplied, just listed the missions in the file for the next 7 days
            if missionDate == None and missionMaker == None and missionName == None:
                with open(missionsFile, 'rt') as csvfile:
                    reader = csv.reader(csvfile, delimiter=',')
                    for row in reader:
                        if datetime.datetime.strptime(row[1], '%m/%d/%y') >= today and datetime.datetime.strptime(row[1], '%m/%d/%y') <= daysAhead:
                            missionFound = True
                            embed = discord.Embed(title="Mission: {}".format(row[0]), color=0x008000)
                            embed.add_field(name="Name", value = row[0], inline=False)
                            embed.add_field(name="Date", value = row[1], inline=False)
                            embed.add_field(name="Time", value = row[2], inline=False)
                            if row[4] != '':
                                embed.add_field(name="Recon", value = row[4], inline=False)
                            
                            embed.add_field(name="Author", value = row[3], inline=False)
                            embed.set_image(url='https://i.imgur.com/M2QQFy1.png')
                            await ctx.send(embed=embed)
                        else:
                            #if the loop finds a mission we want to leave it at true, if not, set it to false
                            if missionFound:
                                missionFound = True
                            else:
                                missionFound = False
            #else if misison date is supplied, list the mission with the cooresponding date
            elif missionDate != None:
                with open(missionsFile, 'rt') as csvfile:
                    reader = csv.reader(csvfile, delimiter=',')
                    for row in reader:
                        if missionDate == row[1]:
                            missionFound = True
                            embed = discord.Embed(title="Mission: {}".format(row[0]), color=0x008000)
                            embed.add_field(name="Name", value = row[0], inline=False)
                            embed.add_field(name="Date", value = row[1], inline=False)
                            embed.add_field(name="Time", value = row[2], inline=False)
                            if row[4] != '':
                                embed.add_field(name="Recon", value = row[4], inline=False)
                            
                            embed.add_field(name="Author", value = row[3], inline=False)
                            embed.set_image(url='https://i.imgur.com/M2QQFy1.png')
                            await ctx.send(embed=embed)
                        else:
                            #if the loop finds a mission we want to leave it at true, if not, set it to false
                            if missionFound:
                                missionFound = True
                            else:
                                missionFound = False
            elif missionName !=None:
                with open(missionsFile, 'rt') as csvfile:
                    reader = csv.reader(csvfile, delimiter=',')
                    for row in reader:
                        if missionName == row[0]:
                            missionFound = True
                            embed = discord.Embed(title="Mission: {}".format(row[0]), color=0x008000)
                            embed.add_field(name="Name", value = row[0], inline=False)
                            embed.add_field(name="Date", value = row[1], inline=False)
                            embed.add_field(name="Time", value = row[2], inline=False)
                            if row[4] != '':
                                embed.add_field(name="Recon", value = row[4], inline=False)
                            
                            embed.add_field(name="Author", value = row[3], inline=False)
                            embed.set_image(url='https://i.imgur.com/M2QQFy1.png')
                            await ctx.send(embed=embed)
                        else:
                            #if the loop finds a mission we want to leave it at true, if not, set it to false
                            if missionFound:
                                missionFound = True
                            else:
                                missionFound = False
            elif missionMaker !=None:
                with open(missionsFile, 'rt') as csvfile:
                    reader = csv.reader(csvfile, delimiter=',')
                    for row in reader:
                        if missionMaker == row[3]:
                            missionFound = True
                            embed = discord.Embed(title="Mission: {}".format(row[0]), color=0x008000)
                            embed.add_field(name="Name", value = row[0], inline=False)
                            embed.add_field(name="Date", value = row[1], inline=False)
                            embed.add_field(name="Time", value = row[2], inline=False)
                            if row[4] != '':
                                embed.add_field(name="Recon", value = row[4], inline=False)
                            
                            embed.add_field(name="Author", value = row[3], inline=False)
                            embed.set_image(url='https://i.imgur.com/M2QQFy1.png')
                            await ctx.send(embed=embed)
                        else:
                            #if the loop finds a mission we want to leave it at true, if not, set it to false
                            if missionFound:
                                missionFound = True
                            else:
                                missionFound = False
                
            if not missionFound:
                embed = discord.Embed(title="Mission: {} was not found".format(missionName), description = "Either you spell like Friedel or it ain't there", color=0xff0000)
                embed.set_image(url='https://i.imgur.com/M2QQFy1.png')
                await ctx.send(embed=embed)

def setup (client):
    client.add_cog(missions(client))
import pycord
import time
from discord.ext import commands
import server_info

#This file should contain all things related to the music module


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guilds_info = {}

    @commands.command()
    async def join(self, ctx):
        """Join your current voice channel"""
        # If user not connected to a VC
        if not (ctx.author.voice):
            await ctx.channel.send('I do not see you in a VC')
            return False
        # If beatbot connected to another VC in that server
        elif (ctx.guild.id in self.guilds_info):
            # If beatbot in the same channel as requester
            if (self.guilds_info[ctx.guild.id].channel() == ctx.author.voice.channel):
                return True
            else:
                await ctx.channel.send('I am already in another VC')
                return False
        else:
            self.guilds_info[ctx.guild.id] = server_info.Server(ctx.guild.id)
            await self.guilds_info[ctx.guild.id].join(ctx)            

    @commands.command()
    async def leave(self, ctx):
        """Leave the current VC. This will Reset the queue."""

        if ctx.voice_client:
            await self.guilds_info[ctx.guild.id].disconenct_vc()
            del self.guilds_info[ctx.guild.id]
        else:
            await ctx.channel.send('I am not in a VC')

    @commands.command()
    async def play(self, ctx, *, search_term):
        """Works with links and search terms"""
        

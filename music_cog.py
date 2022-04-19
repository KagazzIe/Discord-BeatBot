import pycord
import time
from discord.ext import commands

#TODO: Find a better name for this
import server_info

#This file should contain all things related to the music module


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guilds_info = {}

    @commands.command()
    async def join(self, ctx):
        # Attempt to join a voice channel
        # Error msgs:
        # 1 = User is not in a call
        # 2 = Beatbot is in another call
        """Join your current voice channel"""
        guild_instance = self.guilds_info.get(ctx.guild.id)
        
        # If user not connected to a VC
        if not (ctx.author.voice):
            await ctx.channel.send('I do not see you in a VC')
            return 1
        # If beatbot connected to another VC in that server
        elif (guild_instance):
            # If beatbot in the same channel as requester
            if (guild_instance.channel() == ctx.author.voice.channel):
                return 0
            else:
                await ctx.channel.send('I am already in another VC')
                return 2
        else:
            self.guilds_info[ctx.guild.id] = server_info.Server(ctx.guild.id)
            await self.guilds_info[ctx.guild.id].join(ctx)
            return 0
        return -1

    @commands.command()
    async def leave(self, ctx):
        # Attempt leave the current voice channel
        # Error msgs:
        # 1 = Beatbot is not in a VC
        """Leave the current VC. This will Reset the queue."""
        guild_instance = self.guilds_info.get(ctx.guild.id)
        
        if ctx.voice_client:
            await guild_instance.disconenct_vc()
            del self.guilds_info[ctx.guild.id]
            return 0
        else:
            await ctx.channel.send('I am not in a VC')
            return 1

    @commands.command()
    async def play(self, ctx, *, search_term):
        """Works with links and search terms"""
        

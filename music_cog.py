import pycord
import time
from discord.ext import commands

#TODO: Find a better name for this
import server_info

#This file should contain all things related to the music module


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guilds_dict = {}

    @commands.command()
    async def join(self, ctx):
        # Attempt to join a voice channel
        """Join your current voice channel"""
        
        session = server_info.Session(ctx.guild.id)
        err = await session.join(ctx)
        
        if (err):
            await ctx.channel.send(err)
            return
        
        self.guilds_dict[ctx.guild.id] = session

    @commands.command()
    async def leave(self, ctx):
        # Attempt leave the current voice channel
        """Leave the current VC. This will Reset the queue."""
        
        if ctx.guild.id not in self.guilds_dict:
            # No session in guild
            return
        
        guild_instance = self.guilds_dict.get(ctx.guild.id)
        err = await guild_instance.disconenct_vc()
        if (err):
            await ctx.channel.send(err)
            return
        del self.guilds_dict[ctx.guild.id]

    @commands.command()
    async def play(self, ctx, *, search_term):
        # Attempt to play a song
        """Works with links and search terms"""
        guild_instance = self.guilds_dict.get(ctx.guild.id)

        if (join(ctx) != 0):
            # Error when joining call
            return 1

        # Create the song object
        # Add song to the guild's song queue
        



































        

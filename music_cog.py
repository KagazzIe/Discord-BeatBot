import pycord
from discord.ext import commands

#TODO: Find a better name for these
import server_info
import song_queue

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
            return err
        
        self.guilds_dict[ctx.guild.id] = session
        return

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
            return err
        del self.guilds_dict[ctx.guild.id]
        return

    @commands.command()
    async def play(self, ctx, *, search_str):
        # Attempt to play a song
        """Works with links and search terms"""
        if (await self.join(ctx)):
            # Error when joining call
            return 1
        
        guild_instance = self.guilds_dict.get(ctx.guild.id)
        
        if is_link(search_str):
            song = song_queue.Song.from_url(search_str, download=True)
        print(song.title)
        ctx.voice_client.play(song, after=None)
        # Add song to the guild's song queue
        














def is_link(string):
    return True




















        

import pycord
from discord.ext import commands
import session_object
import song_objects
import ytdl_config

#This file should contain all things related to the music module


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guilds_dict = {}

    @commands.command()
    async def join(self, ctx):
        # Attempt to join a voice channel
        """Join your current voice channel"""
        
        guild_instance = session_object.Session(ctx.guild.id)
        err = await guild_instance.join(ctx)
        
        if (err):
            await ctx.channel.send(err)
            return err
        
        self.guilds_dict[ctx.guild.id] = guild_instance
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

        if (ctx.guild.id not in self.guilds_dict):
            err = await self.join(ctx)
            if (err):
                # Error when joining call
                print(err)
                return
        
        guild_instance = self.guilds_dict.get(ctx.guild.id)
        
        if is_link(search_str):
            song = song_objects.Song(search_str, ytdl_config.ytdl_url)

        guild_instance.add_song(song)

        if (not guild_instance.currently_playing):
            guild_instance.play_next()
        














def is_link(string):
    return True




















        

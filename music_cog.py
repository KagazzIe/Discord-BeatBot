import pycord
from discord.ext import commands
import session_object
import queue_elements
import ytdl_config
import asyncio
# This file should contain all things related to the music module

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guilds_dict = {}

    async def close_session(self, guild_id):
        guild_instance = self.guilds_dict.get(guild_id)
        await guild_instance.disconenct_vc()
        del self.guilds_dict[guild_id]

    @commands.command()
    async def join(self, ctx):
        # Attempt to join a voice channel

        guild_instance = session_object.Session(ctx.guild.id, self.close_session)
        err = await guild_instance.join(ctx)

        if (err):
            await ctx.channel.send(err)
            return err

        self.guilds_dict[ctx.guild.id] = guild_instance
        return

    @commands.command()
    async def leave(self, ctx):
        # Attempt leave the current voice channel

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
        # If someone beat bot is not a in a voice channel,
        #   then join the user's vc
        # Download thier song, add it to the queue, and start the
        # next_song() loop if it is not already running

        if (ctx.guild.id not in self.guilds_dict):
            err = await self.join(ctx)
            if (err):
                # Error when joining call
                print(err)
                return

        guild_instance = self.guilds_dict.get(ctx.guild.id)

        if is_link(search_str):
            config = ytdl_config.ytdl_url
        else:
            config = ytdl_config.ytdl_search
        song = queue_elements.Song(search_str, config, ctx.author.id)

        guild_instance.add_song(song)

        if (not guild_instance.currently_playing):
            await guild_instance.play_next(asyncio.get_running_loop())

    @commands.command()
    async def skip(self, ctx):
        #Skip the song that is currently playing
        if (ctx.guild.id not in self.guilds_dict):
            return
        guild_instance = self.guilds_dict.get(ctx.guild.id)
        if (guild_instance.currently_playing):
            await ctx.channel.send("Skipping Song :fast_forward:")
            ctx.voice_client.stop()
        else:
            await ctx.channel.send("Not playing in a VC")

    @commands.command()
    async def queue(self, ctx):
        #Send a list of all current songs in chat
        if (ctx.guild.id not in self.guilds_dict):
            return

        guild_instance = self.guilds_dict.get(ctx.guild.id)
        await ctx.channel.send(guild_instance.song_queue_str())


def is_link(string):
    return string.startswith("https://www.youtube.com/watch?v=")
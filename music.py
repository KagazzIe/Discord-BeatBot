import discord
import youtube_dl
import time
from discord.ext import commands
import queue
#Youtube DL Needed
#Discord Library Needed

# These options are originally from
# https://stackoverflow.com/questions/66070749/how-to-fix-discord-music-bot-that-stops-playing-before-the-song-is-actually-over
ytdl_format_options = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'default_search': 'auto'
}
ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

ffmpeg_options = {
    'options': '-vn',
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
}
class Song(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=1):
        super().__init__(source, volume)
        self.data = data
        self.url = data.get('url')

    @classmethod
    async def search(self, search_term):
        data = ytdl.extract_info("ytsearch:{%s}" % search_term, download=False)['entries'][0]
        return self(discord.FFmpegPCMAudio(data['url'], **ffmpeg_options), data=data)        

class Music(commands.Cog):
    # I eventually want to get this running on a linux machine so I can fork
    # This would allow extremly easy VC management
    # Because I am on windows I need to murder this bueatiful code
    def __init__(self, bot):
        self.bot = bot
        self.guild_song_lists = {}

    @commands.command()
    async def join(self, ctx):
        channel = ctx.author.voice.channel
        if channel is None:
            print("User is not in a channel")
            return
        if ctx.voice_client is not None:
            await ctx.voice_client.move_to(channel)
        else:
            self.guild_song_lists[ctx.guild.id] = queue.Queue()
            await channel.connect()

    @commands.command()
    async def leave(self, ctx):
        if ctx.voice_client is not None:
            self.guild_song_lists[ctx.guild.id] = None
            await ctx.channel.send("Leaving VC :wave:")
            await ctx.voice_client.disconnect()
        else:
            print("User is not in a channel")

    @commands.command()
    async def play(self, ctx, *, search_term):
        def next_song(guild_id, voice_client):
            song_queue = self.guild_song_lists[ctx.guild.id]
            if song_queue and (not voice_client.is_playing()):
                ctx.voice_client.play(song_queue.get(), after=lambda x: next_song(guild_id, voice_client))
        # If Beatbot is currently playing music in a channel that the requester is not in      
        if (ctx.guild.id in self.guild_song_lists) and ctx.voice_client.is_playing() and (ctx.author.voice.channel != ctx.voice_client.channel):
            await ctx.channel.send("I am currently playing music in: %s" % ctx.voice_client.channel.name)
            return
        await self.join(ctx)
        await ctx.channel.send("Searching :mag_right: `%s`" % search_term)
        player = await Song.search(search_term)
        await ctx.channel.send("Added video #%i to queue :file_folder: %s" % (self.guild_song_lists[ctx.guild.id].qsize()+ctx.voice_client.is_playing(), player.data.get('title')))
        self.guild_song_lists[ctx.guild.id].put(player)
        next_song(ctx.guild.id, ctx.voice_client)
        
    
    @commands.command()
    async def pause(self, ctx):
        if ctx.voice_client:
            await ctx.channel.send("Skipping Song :pause_button:")
            ctx.voice_client.pause()
        else:
            ctx.channel.send("I am not connected to a VC")

    @commands.command()
    async def resume(self, ctx):
        if ctx.voice_client:
            await ctx.channel.send("Resuming Song :arrow_right:")
            ctx.voice_client.resume()
        else:
            ctx.channel.send("I am not connected to a VC")

    @commands.command()
    async def stop(self, ctx):
        if ctx.voice_client:
            await ctx.channel.send("Stoping Music :stop_button:")
            self.song_list = []
            ctx.voice_client.stop()
        else:
            ctx.channel.send("I am not connected to a VC")
        
    @commands.command()
    async def skip(self, ctx):
        if ctx.voice_client:
            await ctx.channel.send("Skipping Song :fast_forward:")
            ctx.voice_client.stop()
        else:
            ctx.channel.send("I am not connected to a VC")

    @commands.command()
    async def queue(self, ctx):
        if ctx.guild.id not in self.guild_song_lists:
            await ctx.channel.send("Not currently connected to a VC")
            return
        if self.guild_song_lists[ctx.guild.id].empty():
            await ctx.channel.send("No songs are currently in queue")
            return
        
        string = "```"
        song_list = list(self.guild_song_lists[ctx.guild.id].queue)
        for i in range(len(song_list)):
            string += "%i - %s\n" % (i, song_list[i].data.get('title'))
        string += "```"
        await ctx.channel.send(string)
        

    

import discord
import youtube_dl
import time
from discord.ext import commands
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
    def __init__(self, bot):
        self.bot = bot
        self.song_list = []

    @commands.command()
    async def join(self, ctx):
        channel = ctx.author.voice.channel
        if channel is None:
            print("User is not in a channel")
            return
        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)
        await channel.connect()

    @commands.command()
    async def leave(self, ctx):
        if ctx.voice_client is not None:
            await ctx.channel.send("Leaving VC :wave:")
            await ctx.voice_client.disconnect()
        else:
            print("User is not in a channel")

    @commands.command()
    async def play(self, ctx, *, search_term):
        def next_song(voice_client):
            if self.song_list and (not voice_client.is_playing()):
                ctx.voice_client.play(self.song_list.pop(0), after=lambda x: next_song(voice_client))
        await self.join(ctx)
        await ctx.channel.send("Searching :mag_right: %s" % search_term)
        player = await Song.search(search_term)
        await ctx.channel.send("Added video #%i to queue :file_folder: %s" % (len(self.song_list)-ctx.voice_client.is_playing(), player.data.get('title')))
        self.song_list.append(player)
        next_song(ctx.voice_client)
        
    
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

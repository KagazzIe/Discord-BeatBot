import discord
import youtube_dl
import time
from discord.ext import commands
import queue
#Youtube DL Needed
#Discord Library Needed

# These options are originally from
# https://stackoverflow.com/questions/66070749/how-to-fix-discord-music-bot-that-stops-playing-before-the-song-is-actually-over
ytdl_format_options_search = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'default_search': 'auto'
}
ytdl_search = youtube_dl.YoutubeDL(ytdl_format_options_search)

ytdl_format_options_link = {
    'format': 'bestaudio/best',
    'noplaylist': False
}
ytdl_link = youtube_dl.YoutubeDL(ytdl_format_options_link)

ffmpeg_options = {
    'options': '-vn',
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'
}

class myQueue(queue.Queue):
    def peek(self):
        return self.queue[0]

class Song(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=1):
        super().__init__(source, volume)
        self.data = data
        self.url = data.get('url')

    @classmethod
    async def search(self, search_term):
        data = ytdl_search.extract_info('ytsearch:{%s}' % search_term, download=False)['entries'][0]
        return self(discord.FFmpegPCMAudio(data['url'], **ffmpeg_options), data=data)

    @classmethod
    async def fetch_link(self, search_term):
        data = ytdl_link.extract_info(search_term, download=False)
        return self(discord.FFmpegPCMAudio(data['url'], **ffmpeg_options), data=data)

    def __len__(self):
        return 1

class Playlist():
    def __init__(self, data):
        self.data = data
        self.song_queue = myQueue()
        for entry in self.data['entries']:
            self.song_queue.put(Song(discord.FFmpegPCMAudio(entry['url'], **ffmpeg_options), data=entry))
        self.title = self.data.get('title')

    @classmethod
    async def search(self, search_term):
        data = ytdl_link.extract_info(search_term, download=False)
        return self(data)

    def change_song(self):
        self.song_queue.get()

    def empty(self):
        return self.song_queue.empty()

    def peek(self):
        return self.song_queue.peek()

    def __len__(self):
        return self.song_queue.qsize()

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guild_song_lists = {}

    @commands.command()
    async def join(self, ctx):
        channel = ctx.author.voice.channel
        if channel is None:
            print('User is not in a channel')
            return
        if ctx.voice_client is not None:
            await ctx.voice_client.move_to(channel)
        else:
            self.guild_song_lists[ctx.guild.id] = myQueue()
            await channel.connect()

    @commands.command()
    async def leave(self, ctx):
        if ctx.voice_client is not None:
            self.guild_song_lists[ctx.guild.id] = None
            await ctx.channel.send('Leaving VC :wave:')
            await ctx.voice_client.disconnect()
        else:
            print('User is not in a channel')

    @commands.command()
    async def play(self, ctx, *, search_term):
        def next_song(guild_id, voice_client):
            song_queue = self.guild_song_lists[ctx.guild.id]
            old_player = song_queue.peek()
            if (isinstance(old_player, Playlist) and (len(old_player)!=1)):
                old_player.change_song()
                new_video = old_player.peek()
            else:
                song_queue.get()
                new_video = song_queue.peek()
            
            if (not song_queue.empty()) and (not voice_client.is_playing()):
                ctx.voice_client.play(new_video, after=lambda x: next_song(guild_id, voice_client))
                
        # If Beatbot is currently playing music in a channel that the requester is not in      
        if (ctx.voice_client) and ctx.voice_client.is_playing() and (ctx.author.voice.channel != ctx.voice_client.channel):
            await ctx.channel.send('I am currently playing music in: %s' % ctx.voice_client.channel.name)
            return
        
        await self.join(ctx)
        
        #Playlist
        if (('&list=' in search_term) and ('https://www.youtube.com/watch?v=' == search_term[:32])):
            await ctx.channel.send('Getting Playlist at link :movie_camera: `%s`' % search_term)
            playlist = await Playlist.search(search_term)
            self.guild_song_lists[ctx.guild.id].put(playlist)
            await ctx.channel.send('Added %i videos to queue :file_folder: %s' % (len(playlist), playlist.title))
            ctx.voice_client.play(self.guild_song_lists[ctx.guild.id].peek().peek(), after=lambda x: next_song(ctx.guild.id, ctx.voice_client))

        #Link
        elif ('https://www.youtube.com/watch?v=' == search_term[:32]):
            await ctx.channel.send('Getting video at link :arrow_right: `%s`' % search_term)
            player = await Song.fetch_link(search_term)
            
            await ctx.channel.send('Added video to queue :file_folder: %s' % (player.data.get('title')))
            self.guild_song_lists[ctx.guild.id].put(player)

        #Search Term
        else:
            await ctx.channel.send('Searching :mag_right: `%s`' % search_term)
            player = await Song.search(search_term)
            await ctx.channel.send('Added video to queue :file_folder: %s' % (player.data.get('title')))
            self.guild_song_lists[ctx.guild.id].put(player)
        
        if (not ctx.voice_client.is_playing()):
            ctx.voice_client.play(self.guild_song_lists[ctx.guild.id].peek(), after=lambda x: next_song(ctx.guild.id, ctx.voice_client))
        
    
    @commands.command()
    async def pause(self, ctx):
        if ctx.voice_client:
            await ctx.channel.send('Pausing Song :pause_button:')
            ctx.voice_client.pause()
        else:
            ctx.channel.send('I am not connected to a VC')

    @commands.command()
    async def resume(self, ctx):
        if ctx.voice_client:
            await ctx.channel.send('Resuming Song :arrow_right:')
            ctx.voice_client.resume()
        else:
            ctx.channel.send('I am not connected to a VC')

    @commands.command()
    async def stop(self, ctx):
        if ctx.voice_client:
            await ctx.channel.send('Stoping Music :stop_button:')
            self.guild_song_lists[ctx.guild.id] = myQueue()
            ctx.voice_client.stop()
        else:
            ctx.channel.send('I am not connected to a VC')
        
    @commands.command()
    async def skip(self, ctx):
        if ctx.voice_client:
            await ctx.channel.send('Skipping Song :fast_forward:')
            ctx.voice_client.stop()
        else:
            ctx.channel.send('I am not connected to a VC')

    @commands.command()
    async def queue(self, ctx):
        if not ctx.voice_client:
            await ctx.channel.send('Not currently connected to a VC')
            return
        if self.guild_song_lists[ctx.guild.id].empty():
            await ctx.channel.send('No songs are currently in queue')
            return
        
        string = '```'
        song_list = list(self.guild_song_lists[ctx.guild.id].queue)
        old_count = 0
        new_count = 0
        for i in range(len(song_list)):
            old_count += 1
            new_count += len(song_list[i])
            if old_count == new_count:
                string += '%i : %s\n' % (new_count, song_list[i].data.get('title'))
            else:
                string += '%i-%i : %s\n' % (old_count, new_count, song_list[i].data.get('title'))
            old_count = new_count
        string += '```'
        await ctx.channel.send(string)

import discord
import youtube_dl
import time
from discord.ext import commands
from collections import deque
# These options are originally from
# https://stackoverflow.com/questions/66070749/how-to-fix-discord-music-bot-that-stops-playing-before-the-song-is-actually-over

ytdl_search = youtube_dl.YoutubeDL({'format': 'bestaudio/best',
                                    'noplaylist': True,
                                    'default_search': 'auto'}
                                   )

ytdl_link = youtube_dl.YoutubeDL({
                                'format': 'bestaudio/best',
                                'noplaylist': False}
                                 )

ytdl_playlist_init = youtube_dl.YoutubeDL({
                                'format': 'bestaudio/best',
                                'noplaylist': False,
                                'playliststart':1,
                                'playlistend':1}
                                 )

playlist_download_batch_size = 5
playlist_download_threshold = 10
ffmpeg_options = {
    'options': '-vn',
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'
}

class Song(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=1):
        super().__init__(source, volume)
        self.data = data
        self.url = data.get('url')
        self.title = data.get('title')

    @classmethod
    async def search(self, search_term):
        data = ytdl_search.extract_info('ytsearch:{%s}' % search_term, download=False)['entries'][0]
        return self(discord.FFmpegPCMAudio(data['url'], **ffmpeg_options), data=data)

    @classmethod
    async def fetch_link(self, search_term):
        data = ytdl_link.extract_info(search_term, download=False)
        return self(discord.FFmpegPCMAudio(data['url'], **ffmpeg_options), data=data)

    #TODO: Make this the length of song, change $play to not rely on it
    def __len__(self):
        return 1

class Playlist():
    def __init__(self, data):
        self.last_batch_data = data
        self.song_deque = deque()
        self.song_deque.append(Song(discord.FFmpegPCMAudio(data['entries'][0]['url'], **ffmpeg_options), data=data['entries'][0]))
        self.title = data.get('title')
        self.index = 2
        self.webpage_url = data['webpage_url']
        self.done_downloading = False

    @classmethod
    async def search(self, search_term):
        data = ytdl_playlist_init.extract_info(search_term, download=False)
        return self(data)

    def change_song(self):
        return self.song_deque.pop()
            
    def get_songs(self):
        if self.done_downloading == True:
            return
        ind = self.index
        self.index += playlist_download_batch_size
        ytdl_temp = youtube_dl.YoutubeDL({
                            'format': 'bestaudio/best',
                            'noplaylist': False,
                            'playliststart':ind,
                            'playlistend':ind+playlist_download_batch_size-1}
                             )
        data = ytdl_temp.extract_info(self.webpage_url, download=False)
        
        if len(data['entries']) != playlist_download_batch_size:
            self.done_downloading = True
        
        
        for entry in data['entries']:
            if self.last_batch_data['entries'][0] == entry:
                self.done_downloading = True
                break
            self.song_deque.append(Song(discord.FFmpegPCMAudio(entry['url'], **ffmpeg_options), data=entry))

        self.last_batch_data = data
        
    def empty(self):
        return True if len(self.song_deque)==0 else False

    def peek(self):
        return self.song_deque[0]

    def __len__(self):
        return len(self.song_deque)

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guild_song_lists = {}
        self.guild_currently_playing = {}
        #self.guild_last_active = {}

    @commands.command()
    async def join(self, ctx):
        channel = ctx.author.voice.channel
        if channel is None:
            print('User is not in a channel')
            return
        if ctx.voice_client is not None:
            await ctx.voice_client.move_to(channel)
        else:
            self.guild_song_lists[ctx.guild.id] = deque()
            self.guild_currently_playing[ctx.guild.id] = None
            await channel.connect()

    @commands.command()
    async def leave(self, ctx):
        if ctx.voice_client is not None:
            self.guild_song_lists[ctx.guild.id] = None
            self.guild_currently_playing[ctx.guild.id] = None
            await ctx.channel.send('Leaving VC :wave:')
            await ctx.voice_client.disconnect()
        else:
            print('User is not in a channel')

    @commands.command()
    async def play(self, ctx, *, search_term):
        def next_song(guild_id, voice_client):
            song_queue = self.guild_song_lists[ctx.guild.id]
            if song_queue == None:
                return
            if len(song_queue) == 0:
                return
            
            player = song_queue[0]
            need_songs = False

            #If it is an empty playlist
            if len(player) == 0:
                song_queue.pop()

            #If the next element is a playlist
            if isinstance(player, Playlist):
                #If the playlist needs to download more songs
                if len(player)<playlist_download_threshold:
                    need_songs = True
                song = player.change_song()
            else:
                song = song_queue.pop()
            self.guild_currently_playing[ctx.guild.id] = song
            if song and (not voice_client.is_playing()):
                ctx.voice_client.play(song, after=lambda x: next_song(guild_id, voice_client))
            if need_songs == True:
                player.get_songs()
                
        # If Beatbot is currently playing music in a channel that the requester is not in      
        if (ctx.voice_client) and ctx.voice_client.is_playing() and (ctx.author.voice.channel != ctx.voice_client.channel):
            await ctx.channel.send('I am currently playing music in: %s' % ctx.voice_client.channel.name)
            return
        
        await self.join(ctx)
        
        #Playlist
        if (('&list=' in search_term) and ('https://www.youtube.com/watch?v=' == search_term[:32])):
            await ctx.channel.send('Getting Playlist at link :movie_camera: `%s`' % search_term)
            playlist = await Playlist.search(search_term)
            self.guild_song_lists[ctx.guild.id].append(playlist)
            await ctx.channel.send('Added playlist to queue :file_folder: %s' % (playlist.title))

        #Link
        elif ('https://www.youtube.com/watch?v=' == search_term[:32]):
            await ctx.channel.send('Getting video at link :arrow_right: `%s`' % search_term)
            player = await Song.fetch_link(search_term)
            
            await ctx.channel.send('Added video to queue :file_folder: %s' % (player.data.get('title')))
            self.guild_song_lists[ctx.guild.id].append(player)

        #Search Term
        else:
            await ctx.channel.send('Searching :mag_right: `%s`' % search_term)
            player = await Song.search(search_term)
            await ctx.channel.send('Added video to queue :file_folder: %s' % (player.data.get('title')))
            self.guild_song_lists[ctx.guild.id].append(player)
        if (not ctx.voice_client.is_playing()):
            next_song(ctx.guild.id, ctx.voice_client)
        
       
    
    @commands.command()
    async def pause(self, ctx):
        if ctx.voice_client and (ctx.author.voice.channel == ctx.voice_client.channel):
            await ctx.channel.send('Pausing Song :pause_button:')
            ctx.voice_client.pause()
        elif ctx.voice_client:
            await ctx.channel.send('You are not in the correct VC')
        else:
            await ctx.channel.send('I am not connected to a VC')

    @commands.command()
    async def resume(self, ctx):
        if ctx.voice_client and (ctx.author.voice.channel == ctx.voice_client.channel):
            await ctx.channel.send('Resuming Song :arrow_right:')
            ctx.voice_client.resume()
        elif ctx.voice_client:
            await ctx.channel.send('You are not in the correct VC')
        else:
            await ctx.channel.send('I am not connected to a VC')

    @commands.command()
    async def stop(self, ctx):
        if ctx.voice_client and (ctx.author.voice.channel == ctx.voice_client.channel):
            await ctx.channel.send('Stoping Music :stop_button:')
            self.guild_song_lists[ctx.guild.id] = deque()
            self.guild_currently_playing[ctx.guild.id] = None
            ctx.voice_client.stop()
        elif ctx.voice_client:
            await ctx.channel.send('You are not in the correct VC')
        else:
            await ctx.channel.send('I am not connected to a VC')
        
    @commands.command()
    async def skip(self, ctx):
        if ctx.voice_client and (ctx.author.voice.channel == ctx.voice_client.channel):
            await ctx.channel.send('Skipping Song :fast_forward:')
            ctx.voice_client.stop()
        elif ctx.voice_client:
            await ctx.channel.send('You are not in the correct VC')
        else:
            await ctx.channel.send('I am not connected to a VC')

    @commands.command()
    async def queue(self, ctx):
        if not ctx.voice_client:
            await ctx.channel.send('Not currently connected to a VC')
            return
        if len(self.guild_song_lists[ctx.guild.id])==0:
            await ctx.channel.send('No songs are currently in queue')
            return

        #here down is aincent code from using queues instead of deques
        #it works but its not optimized for deques
        string = '```'
        song_list = [self.guild_currently_playing[ctx.guild.id]] + list(self.guild_song_lists[ctx.guild.id])

        for i in range(len(song_list)):
            if isinstance(song_list[i], Playlist):
                string += 'On song #%i in: %s\n' % (song_list[i].index-len(song_list[i]), song_list[i].title)
            else:
                string += '%s\n' %(song_list[i].title)
        string += '```'
        await ctx.channel.send(string)
        
    @commands.command()
    async def np(self, ctx):
        if not ctx.voice_client:
            await ctx.channel.send('Not currently connected to a VC')
            return
        if not ctx.voice_client.is_playing():
            await ctx.channel.send('Not currently playing a song')
            return

        current_song = self.guild_currently_playing[ctx.guild.id]
            
        song_name = current_song.data.get('title')
        await ctx.channel.send("Now Listening to:musical_note: %s" % song_name)

    @commands.command()
    async def skip_playlist(self, ctx):
        if ctx.voice_client and (ctx.author.voice.channel == ctx.voice_client.channel):
            await ctx.channel.send('Skipping Songs :fast_forward:')
            song_queue = self.guild_song_lists[ctx.guild.id]
            top_item = song_queue[0]
            if isinstance(top_item, Playlist) and (top_item.index > 2):
                song_queue.pop()
            ctx.voice_client.stop()
        elif ctx.voice_client:
            await ctx.channel.send('You are not in the correct VC')
        else:
            await ctx.channel.send('I am not connected to a VC')
    
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if before.channel and (len(before.channel.members)==1) and (self.bot.user.id in [x.id for x in before.channel.members]):
            if after.channel and (self.bot.user.id in [x.id for x in after.channel.members]):
                return
            print('Leave Call Triggered')
            self.guild_song_lists[before.channel.guild.id] = None
            self.guild_currently_playing[before.channel.guild.id] = None
            await before.channel.guild.voice_client.disconnect()
    

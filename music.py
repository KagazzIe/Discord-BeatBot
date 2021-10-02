import discord
import time
from discord.ext import commands
from music_objects import *



class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guilds_info = {}


    @commands.command()
    async def join(self, ctx):
        """Join your current voice channel"""
        
        if ctx.author.voice is None:
            await ctx.channel.send('I do not see you in a VC')
            return
        channel = ctx.author.voice.channel
        if ctx.voice_client:
            await ctx.voice_client.move_to(channel)
        else:
            self.guilds_info[ctx.guild.id] = Guild_Info()
            await channel.connect()

    @commands.command()
    async def leave(self, ctx):
        """Leave the current VC. This will Reset the queue."""
        if ctx.voice_client is not None:
            self.guilds_info[ctx.guild.id] = None
            await ctx.channel.send('Leaving VC :wave:')
            await ctx.voice_client.disconnect()
        else:
            await ctx.channel.send('I am not in a VC')

    @commands.command()
    async def play(self, ctx, *, search_term):
        """Works with links and search terms"""
        # If Beatbot is currently playing music in a channel that the requester is not in      
        if (ctx.voice_client) and self.guilds_info[ctx.guild.id].current_song and (ctx.author.voice.channel != ctx.voice_client.channel):
            await ctx.channel.send('I am currently playing music in: %s' % ctx.voice_client.channel.name)
            return
        
        await self.join(ctx)
        s = Song(search_term)
        self.guilds_info[ctx.guild.id].song_queue.add_bottom(s)
        await ctx.channel.send('Added song to queue :file_folder:')
        
        if (not self.guilds_info[ctx.guild.id].current_song):
            self.next_song(ctx.guild.id, ctx.voice_client)

    @commands.command()
    async def top(self, ctx, *, search_term):
        """Add a song to the top of the queue"""
        # If Beatbot is currently playing music in a channel that the requester is not in      
        if (ctx.voice_client) and self.guilds_info[ctx.guild.id].current_song and (ctx.author.voice.channel != ctx.voice_client.channel):
            await ctx.channel.send('I am currently playing music in: %s' % ctx.voice_client.channel.name)
            return
        
        await self.join(ctx)
        s = Song(search_term)
        self.guilds_info[ctx.guild.id].song_queue.add_top(s)
        await ctx.channel.send('Added song to queue :file_folder:')
        if (not self.guilds_info[ctx.guild.id].current_song):
            self.next_song(ctx.guild.id, ctx.voice_client)

    @commands.command()
    async def play_playlist(self, ctx, *, search_term):
        """This will play an entire playlist of songs
        Either link a song in the playlist or link the playlist itself.
        There is no search feature for playlists"""
        await self.join(ctx)
        if (('&list=' not in search_term) or ('https://www.youtube.com/watch?v=' != search_term[:32])):
            await ctx.channel.send('I can\'t recognize this playlist link')
        p = Playlist(search_term)
        self.guilds_info[ctx.guild.id].song_queue.add_bottom(p)
        await ctx.channel.send('Added playlist to queue :file_folder:')
        if (not self.guilds_info[ctx.guild.id].current_song):
            self.next_song(ctx.guild.id, ctx.voice_client)

    @commands.command()
    async def top_playlist(self, ctx, *, search_term):
        """Add a playlist to the top of the queue"""
        await self.join(ctx)
        if (('&list=' not in search_term) or ('https://www.youtube.com/watch?v=' != search_term[:32])):
            await ctx.channel.send('I can\'t recognize this playlist link')
        p = Playlist(search_term)
        self.guilds_info[ctx.guild.id].song_queue.add_top(p)
        await ctx.channel.send('Added playlist to queue :file_folder:')
        if (not self.guilds_info[ctx.guild.id].current_song):
            self.next_song(ctx.guild.id, ctx.voice_client)
    
    @commands.command()
    async def pause(self, ctx):
        """Pause the current song"""
        if ctx.voice_client and (ctx.author.voice.channel == ctx.voice_client.channel):
            await ctx.channel.send('Pausing Song :pause_button:')
            ctx.voice_client.pause()
        elif ctx.voice_client:
            await ctx.channel.send('You are not in the correct VC')
        else:
            await ctx.channel.send('I am not connected to a VC')

    @commands.command()
    async def resume(self, ctx):
        """Resume from the paused state"""
        if ctx.voice_client and (ctx.author.voice.channel == ctx.voice_client.channel):
            await ctx.channel.send('Resuming Song :arrow_right:')
            ctx.voice_client.resume()
        elif ctx.voice_client:
            await ctx.channel.send('You are not in the correct VC')
        else:
            await ctx.channel.send('I am not connected to a VC')

    @commands.command()
    async def stop(self, ctx):
        """Stop playing music and clear the song queue"""
        if ctx.voice_client and (ctx.author.voice.channel == ctx.voice_client.channel):
            await ctx.channel.send('Stoping Music :stop_button:')
            self.guilds_info[ctx.guild.id] = Guild_Info()
            ctx.voice_client.stop()
        elif ctx.voice_client:
            await ctx.channel.send('You are not in the correct VC')
        else:
            await ctx.channel.send('I am not connected to a VC')
    
    @commands.command()
    async def skip(self, ctx):
        """Skip the current song"""
        if ctx.voice_client and (ctx.author.voice.channel == ctx.voice_client.channel):
            await ctx.channel.send('Skipping Song :fast_forward:')
            ctx.voice_client.stop()
        elif ctx.voice_client:
            await ctx.channel.send('You are not in the correct VC')
        else:
            await ctx.channel.send('I am not connected to a VC')

    @commands.command()
    async def skip_playlist(self, ctx):
        """Skip the current song. If the current song is in a playlist, then remove the playlist from the queue"""
        if ctx.voice_client and (ctx.author.voice.channel == ctx.voice_client.channel):
            await ctx.channel.send('Skipping Songs :fast_forward:')
            self.guilds_info[ctx.guild.id].song_queue.remove_element(0)
            ctx.voice_client.stop()
        elif ctx.voice_client:
            await ctx.channel.send('You are not in the correct VC')
        else:
            await ctx.channel.send('I am not connected to a VC')

    @commands.command()
    async def remove(self, ctx, *, n):
        """Removes Nth element from queue"""
        if ctx.voice_client and (ctx.author.voice.channel == ctx.voice_client.channel):
            await ctx.channel.send('Deleting Song :boom:')
            self.guilds_info[ctx.guild.id].song_queue.remove_element(int(n))
            if n == 0:
                ctx.voice_client.stop()
        elif ctx.voice_client:
            await ctx.channel.send('You are not in the correct VC')
        else:
            await ctx.channel.send('I am not connected to a VC')
    
    @commands.command()
    async def queue(self, ctx):
        """Show the current song queue"""
        if not ctx.voice_client:
            await ctx.channel.send('Not currently connected to a VC')
            return
        if (len(self.guilds_info[ctx.guild.id].song_queue)==0) and (not self.guilds_info[ctx.guild.id].current_song):
            await ctx.channel.send('No songs are currently in queue')
            return
        if ctx.voice_client.is_playing():
            string = 'Playing'
        else:
            string = 'Paused'
        string += str(self.guilds_info[ctx.guild.id].song_queue)
        await ctx.channel.send(string)
    
    @commands.command()
    async def np(self, ctx):
        """Show the song that is currently playing"""
        if not ctx.voice_client:
            await ctx.channel.send('Not currently connected to a VC')
            return
        if not ctx.voice_client.is_playing():
            await ctx.channel.send('Not currently playing a song')
            return

        current_song = self.guilds_info[ctx.guild.id].current_song.song_title
        await ctx.channel.send("Now Listening to:musical_note: %s" % current_song)
    
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if before.channel and (len(before.channel.members)==1) and (self.bot.user.id in [x.id for x in before.channel.members]):
            if after.channel and (self.bot.user.id in [x.id for x in after.channel.members]):
                return
            ('Leave Call Triggered')
            self.guilds_info[before.channel.guild.id] = None
            await before.channel.guild.voice_client.disconnect()

    def next_song(self, guild_id, voice_client):
        curframe = inspect.currentframe()
        calframe = inspect.getouterframes(curframe, 2)
        #print('next_song caller name:' + calframe[1][3])
        song_queue = self.guilds_info[guild_id].song_queue

        preloaded_count = len(song_queue)
        if preloaded_count == 0:
            preloaded_count += 1
            song_queue.download(1)
        song = song_queue.change_song()
        preloaded_count -= 1
        
        if song and (not voice_client.is_playing()):
            voice_client.play(song, after=lambda x: self.next_song(guild_id, voice_client))
        if preloaded_count < song_queue.min_buffer:
            song_queue.download(song_queue.batch_size)
    

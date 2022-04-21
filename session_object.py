import song_objects

class Session():
    # Sever contains the discordpy api guild and any other
    # extra data that we would want to associate with a server
    def __init__(self, server_id):
        self.id = server_id
        self.voice_client = None
        self.voice_channel = None
        self.song_queue = song_objects.Song_Queue(preload_count = 1)
        self.currently_playing = False
        
    async def join(self, ctx):
        # Try to connect to the voice channel that is found in ctx
        try:
            await ctx.author.voice.channel.connect()
        # TODO: Add different except to allow bot to leave current call to join the user's vc
        except AttributeError as e:
            return "I cannot see you in a VC"
        except Exception as e:
            return str(e)
        self.voice_client = ctx.voice_client
        self.voice_channel = ctx.author.voice.channel
        
        return 0

    async def disconenct_vc(self):
        # Try to disconnect from the active VC
        try:
            await self.voice_client.disconnect()
        except Exception as e:
            print(type(e))
            return str(e)
        self.voice_client = None
        self.voice_channel = None

        return 0

    def play_next(self):
        """
        This works by playing the next song, then using the voice_client.play 
        after argument to call the function again after the song is over.
        This creates a loop which allows songs to play one after another.
        
        I ran into a lot of issues in the last iteration of beat bot with two 
        independent play_next() loops being started which caused different bugs.

        Setting self.currently_playing immediatley to true, and checking
        it before  $play starts a new play_next loop should fix most of these issues. I think.
        """
        self.currently_playing = True
        next_song = self.song_queue.change_song()
        if next_song:
            self.voice_client.play(next_song, after=lambda x: self.play_next())
        else:
            self.currently_playing = False

    def add_song(self, song):
        self.song_queue.append(song)

    def song_queue_str(self):
        if (not self.currently_playing):
            return "There are no songs in queue"

        final_string = "Currently Playing: "
        final_string += self.song_queue.current_song.title + "\n\n"

        for i in range(len(self.song_queue)):
            final_string += str(i+1)+ ". " +self.song_queue[i].title + "\n"
        
        return final_string
        
    def __eq__(self, other):
        # returns true when other is equal to the server id
        return (self.id == other)
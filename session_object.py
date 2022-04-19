import song_objects

class Session():
    # Sever contains the discordpy api guild and any other
    # extra data that we would want to associate with a server
    def __init__(self, server_id):
        self.id = server_id
        self.voice_client = None
        self.voice_channel = None
        self.song_queue = song_objects.Song_Queue(preload_count = 1)
        
    async def join(self, ctx):
        # Try to connect to the voice channel that is found in ctx
        try:
            await ctx.author.voice.channel.connect()
        # TODO: Add different except to allow bot to leave current call to join the user's vc
        except AttributeError as e:
            # When the user is not in a VC
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

    def __eq__(self, other):
        # returns true when other is equal to the server id
        return (self.id == other)



import pycord

class Server():
    # Sever contains the discordpy api guild and any other
    # extra data that we would want to associate with a server
    def __init__(self, server_id):
        self.id = server_id
        self.voice_client = None
        self.voice_channel = None

    async def join(self, ctx):
        # Try to connect to the voice channel that is found in ctx
        try:
            await ctx.author.voice.channel.connect()
        except Exception as e:
            print('Error joining VC')
            print(e)
            return False
        self.voice_client = ctx.voice_client
        self.voice_channel = ctx.author.voice.channel
        
        return True

    async def disconenct_vc(self):
        # Try to disconnect from the active VC
        try:
            await self.voice_client.disconnect()
        except Exception as e:
            print('Error leaving VC')
            print(e)
            return False
        self.voice_client = None
        self.voice_channel = None
        return True

    def vc(self):
        return self.voice_client

    def channel(self):
        return self.channel

    def __eq__(self, other):
        #returns true when other is equal to the server id
        return (self.id == other)

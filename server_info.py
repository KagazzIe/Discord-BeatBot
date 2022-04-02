import discord

class Server():
    # Sever contains the discordpy api guild and any other
    # extra data that we would want to associate with a server
    def __init__(self, server_id):
        self.id = server_id
        self.vc = None

    async def join(self, ctx):
        # Try to connect to the voice channel that is found in ctx
        try:
            await ctx.author.voice.channel.connect()
        except Exception as e:
            print('Error joining VC')
            print(e)
            return False
        self.vc = ctx.voice_client
        return True

    async def disconenct_vc(self):
        # Try to disconnect from the active VC
        try:
            await self.vc.disconnect()
        except Exception as e:
            print('Error leaving VC')
            print(e)
            return False
        self.active_vc = None
        return True

    def return_song_queue(self):
        # Return the song_queue object to the caller
        pass

    def __eq__(self, other):
        #returns true when other is equal to the server id
        return (self.id == other)

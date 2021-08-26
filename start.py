import discord
import os
import youtube_dl
import time

#PyNaCl Library Needed
#Discord Library Needed
#Youtube DL Needed



# These options are originally from
# https://stackoverflow.com/questions/66070749/how-to-fix-discord-music-bot-that-stops-playing-before-the-song-is-actually-over
ytdl_format_options = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'default_search': 'auto',
    'nocheckcertificate': True,
    'logtostderr': False,
    'quiet': True,
}

ffmpeg_options = {
    'options': '-vn',
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)
guild_queues = {}
bot = discord.Client()
class myBot():
    pass
class Song():
    def __init__(self, bot_url, user_url, title, response_channel_id, requester_name):
        self.bot_url = bot_url
        self.user_url = user_url
        self.title = title
        self.channel_id = response_channel_id
        self.requester_name = requester_name

async def join_channel(message):
    for channel in message.guild.voice_channels:
        channel_members = [x.id for x in channel.members]
        if (message.author.id in channel_members):
            if bot.user.id not in channel_members:
                #If bot is not in the correct channel
                await leave_channel(message)
                await channel.connect()
                guild_queues[message.guild.id] = []
                stop(message)
        
async def leave_channel(message):
    if message.guild.voice_client:
        guild_queues[message.guild] = None
        await message.guild.voice_client.disconnect()

async def play(message):
    
    await join_channel(message)
    search_term = message.content[5:].strip()
    await message.channel.send("Searching :mag_right: %s" % search_term)
    video = ytdl.extract_info("ytsearch:{%s}" % search_term, download=False)["entries"][0]
    bot_url = video["formats"][0]["url"]
    title = video["title"]
    user_url = "https://www.youtube.com/watch?v=%s" % video["id"]
    song = Song(bot_url, user_url, title, message.channel.id, message.author.display_name)
    queue_len = len(guild_queues[message.channel.id]) + message.guild.voice_client.is_playing()
    guild_queues[message.guild.id].append(song)
    await message.channel.send("Added video #%i queue :file_folder: %s" % (queue_len, title))
    
    play_next(message)

def stop(message):
    if message.guild.voice_client:
        message.guild.voice_client.stop()

def pause(message):
    if message.guild.voice_client:
        message.guild.voice_client.pause()

def resume(message):
    if message.guild.voice_client:
        message.guild.voice_client.resume()

def skip(message):
    if message.guild.voice_client:
        stop(guild)
        play_next(guild)

def play_next(message):
    guild = message.guild
    if (not guild.voice_client.is_playing()) and guild_queues[guild.id]:
        start = time.time()
        song = guild_queues[guild.id][0]
        response_channel = bot.get_channel(song.channel_id)
        guild.voice_client.play(discord.FFmpegPCMAudio(song.bot_url, **ffmpeg_options), after=lambda x:play_next(message))
        guild_queues[guild.id] = guild_queues[guild.id][1:]
        print("Time to format and play song: %s" % str(time.time()-start)) 
    
@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    await_functions = {'$join':join_channel,
                 '$leave':leave_channel,
                 '$play':play}
    
    functions = {'$stop':stop,
                 '$pause':pause,
                 '$resume':resume,
                 '$skip':skip}
    arguments = message.content.split(" ")
    if arguments[0] in await_functions:
        await await_functions[arguments[0]](message)
    elif arguments[0] in functions:
        functions[arguments[0]](message)
    elif message.content.startswith('$'):
        #This is for testing the internals
        print(message.content[1:])
        exec(message.content[1:])



f = open("token.txt", 'r')
token = f.readline().strip()
f.close()

bot.run(token)

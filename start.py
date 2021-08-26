import discord
import os
import youtube_dl
import time

#PyNaCl Library Needed
#Discord Library Needed
#Youtube DL Needed

bot = discord.Client()

# These options are originally from
# https://stackoverflow.com/questions/66070749/how-to-fix-discord-music-bot-that-stops-playing-before-the-song-is-actually-over
ytdl_format_options = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'default_search': 'auto',
    'nocheckcertificate': True,
}

ffmpeg_options = {
    'options': '-vn',
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)
guild_queues = {}
        
async def join_channel(message):
    for channel in message.guild.voice_channels:
        channel_members = [x.id for x in channel.members]
        if (message.author.id in channel_members):
            if bot.user.id not in channel_members:
                #If bot is not in the correct channel
                    await leave_channel(message)
                    await channel.connect()
                    guild_queues[message.guild.id] = []
                    stop(message.guild)
        
async def leave_channel(message):
    if message.guild.voice_client:
        guild_queues[message.guild] = None
        await message.guild.voice_client.disconnect()

async def play(message):
    
    await join_channel(message)
    guild_queues[message.guild.id].append(ytdl.extract_info("ytsearch:{%s}" % message.content[5:].strip(), download=False)["entries"][0]["formats"][0]["url"])
    play_next(message.guild)

def stop(guild):
    if guild.voice_client:
        guild.voice_client.stop()

def pause(guild):
    if guild.voice_client:
        message.guild.voice_client.pause()

def resume(guild):
    if guild.voice_client:
        guild.voice_client.resume()

def skip(guild):
    if guild.voice_client:
        stop(guild)
        time.sleep(0.5) #Sleep for a half second to put a pause between songs
        play_next(guild)

def play_next(guild):
    if (not guild.voice_client.is_playing()) and guild_queues[guild.id]:
        start = time.time()
        next_song = guild_queues[guild.id][0]
        guild.voice_client.play(discord.FFmpegPCMAudio(next_song, **ffmpeg_options), after=lambda x: play_next(guild))
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
        functions[arguments[0]](message.guild)
    elif message.content.startswith('$'):
        #This is for testing the internals
        print(message.content[1:])
        exec(message.content[1:])



f = open("token.txt", 'r')
token = f.readline().strip()
f.close()

bot.run(token)

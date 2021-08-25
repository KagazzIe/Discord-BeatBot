import discord
import os
import youtube_dl
import time

#PyNaCl Library Needed
#Discord Library Needed

bot = discord.Client()

# These options are originally from
#https://stackoverflow.com/questions/66070749/how-to-fix-discord-music-bot-that-stops-playing-before-the-song-is-actually-over
ytdl_format_options = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'nocheckcertificate': True,
}
ffmpeg_options = {
    'options': '-vn',
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
}
ytdl = youtube_dl.YoutubeDL(ytdl_format_options)
 
async def join_channel(message):
    for channel in message.guild.voice_channels:
        channel_members = [x.id for x in channel.members]
        if (message.author.id in channel_members):
            if bot.user.id not in channel_members:
                #If bot is not in the correct channel
                    await leave_channel(message)
                    await channel.connect()
                    stop(message)
        
async def leave_channel(message):
    if message.guild.voice_client:
        await message.guild.voice_client.disconnect()

async def play(message):
    
    await join_channel(message)
    
    start = time.time()
    song_info = ytdl.extract_info(message.content[5:].strip(), download=False)
    print(time.time()-start)
    
    start = time.time()
    message.guild.voice_client.play(discord.FFmpegPCMAudio(song_info["formats"][0]["url"], **ffmpeg_options), after=lambda x: stop(message))
    print(time.time()-start)
    
    message.guild.voice_client.source = discord.PCMVolumeTransformer(message.guild.voice_client.source)
    message.guild.voice_client.source.volume = 1

def stop(message):
    if message.guild.voice_client:
        message.guild.voice_client.stop()

def pause(message):
    if message.guild.voice_client:
        message.guild.voice_client.pause()

def resume(message):
    if message.guild.voice_client:
        message.guild.voice_client.resume()

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
                 '$resume':resume}
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

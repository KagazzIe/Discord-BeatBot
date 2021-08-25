import discord
import os

#PyNaCl Library Needed
#Discord Library Needed

bot = discord.Client()

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # I want to find a more elegent solution to functions
    # Currently I am using this method just to understand how it works
    if message.content.startswith('$join'):
        await join_channel(message)

    elif message.content.startswith('$leave'):
        await leave_channel(message)
        
    elif message.content.startswith('$'):
        #await message.channel.send('Hello!')
        
        #This is for testing the internals
        print(message.content[1:])
        exec(message.content[1:])

async def join_channel(message):
    for channel in message.guild.voice_channels:
        if message.author.id in [x.id for x in channel.members]:
            await leave_channel(message)
            await channel.connect()
            break

async def leave_channel(message):
    if message.guild.voice_client:
        await message.guild.voice_client.disconnect()


f = open("token.txt", 'r')
token = f.readline().strip()
f.close()

bot.run(token)

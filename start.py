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
        for channel in message.guild.voice_channels:
            if message.author.id in [x.id for x in channel.members]:
                current_vc = message.guild.voice_client
                if current_vc:
                    await current_vc.disconnect()
                await channel.connect()
                break

    elif message.content.startswith('$leave'):
        current_vc = message.guild.voice_client
        await current_vc.disconnect()
    elif message.content.startswith('$'):
        #await message.channel.send('Hello!')
        
        #This is for testing the internals
        print(message.content[1:])
        exec(message.content[1:])
    



f = open("token.txt", 'r')
token = f.readline().strip()
f.close()

bot.run(token)

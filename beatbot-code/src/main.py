import pycord
from discord.ext import commands
import os

#my libs
import music_cog


bot = commands.Bot(command_prefix='$', case_insensitive=True)
bot.add_cog(music_cog.Music(bot))

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')
    

f = open(os.path.join(os.path.dirname(__file__), "..", "token.txt"), 'r')
token = f.readline().strip()
f.close()

bot.run(token)

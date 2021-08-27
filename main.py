from discord.ext import commands

#my libs
from music import Music


#PyNaCl Library Needed
#Discord Library Needed


bot = commands.Bot(command_prefix=commands.when_mentioned_or("$"))
bot.add_cog(Music(bot))

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')

f = open("token.txt", 'r')
token = f.readline().strip()
f.close()

bot.run(token)

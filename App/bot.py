# bot.py
import os
import asyncio
import discord
from discord.ext import commands
import logging

#set up a debug log to basic.log file. Flags messages of level INFO and above
#Note: The logconfig text file is not currently in use.
logging.basicConfig(filename="basic.log", filemode="w",
                    level=logging.DEBUG, encoding="utf-8",
                    format='%(levelname)-10s:%(name)-10s:%(message)s')


TOKEN = open(".bottoken.txt", "r").read()

#The client must be a Bot class and not a Client class to
# import the extensions. The message content intent must be manually added
intent = discord.Intents.default()
intent.message_content = True

client = commands.Bot(command_prefix="",
                      intents=intent)

#method to load extensions into client
async def loadall(bot: commands.Bot):
    for filename in os.listdir('./Cogs'):
        if "__init__" in filename:
            pass
        elif filename.endswith('.py'):
                print({filename[:-3]})
                await client.load_extension(f'Cogs.{filename[:-3]}')
                print(f'cogs.{filename[:-3]} loaded')

#what the bot actually does (log on)

async def main():
    async with client:
        await loadall(client)
        await client.start(TOKEN)


asyncio.run(main())
#client.run(TOKEN)
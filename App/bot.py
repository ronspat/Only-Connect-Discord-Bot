# bot.py

import discord

TOKEN = open(".bottoken.txt", "r").read()

client = discord.Client(intents=discord.Intents.default())

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

client.run(TOKEN)
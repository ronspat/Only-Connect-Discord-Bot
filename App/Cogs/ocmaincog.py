import discord
from discord.ext import commands


class OCmaincog(commands.Cog):

    def __init__(self, client):
        self.client = client

    #events
    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self.client.user} has connected to Discord!')

    #commands
    @commands.command()
    async def playoc(self, ctx):
        await ctx.send(f'Hi! Welcome to Only Connect. '
              f'Type .p for a practice round, or .g '
              f'for a full game.')

async def setup(client: commands.Bot):
    await client.add_cog(OCmaincog(client))
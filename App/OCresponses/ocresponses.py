import asyncio
import discord
from discord.ext import commands

class OCresponsemethods:

    #timer method
    async def counttime(cog: commands.Cog, channelid, timelimit, ctx: commands.Context):
        await asyncio.sleep(timelimit)
        cog.client.istimeron[channelid] = False
        #print("Task finished")
        await ctx.send('Sorry you ran out of time!')
        await ctx.send(cog.client.questionsinplay[ctx.channel.id].questioninfo["response"])
        #The timer is started by using it to construct an Asyncio task object
        #with the create task method in asyncio.
        # a specific task.cancel() method is used in methods where the timer is stopped early.
        # If the timer is not stopped early, the code here will continue running beyond the asyncio sleep method
        if cog.client.questionsinplay[ctx.channel.id].questioninfo["novelty"] == "audio":
            await ctx.guild.voice_client.stop()
            await ctx.guild.voice_client.disconnect()

        if cog.client.games[ctx.channel.id] in {"p1", "p2"}:
            await ctx.channel.send("Thanks for playing! Type playoc to try another question.")
            cog.client.games[ctx.channel.id] = "s"

    async def round2question(cog: commands.Cog, ctx: commands.Context):
        if cog.client.games[ctx.channel.id] == "p1" or cog.client.games[ctx.channel.id] == "g1":

            if self.client.commandedkeys[ctx.channel.id] == "2":


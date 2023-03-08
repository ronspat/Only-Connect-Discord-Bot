import operator

import Questions.questions
import discord
from discord.ext import commands
import OCresponses.ocresponses
# for creating a timer
import asyncio


class OCmaincog(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.client.games = {}
        self.client.questionsinplay = {}
        self.client.commandedkeys = {}
        self.client.timertasks = {}
        self.client.istimeron = {}
        self.client.musictasks = {}

    # the client is a Bot object class. I am not sure why it allows you to add new variables to the bot object but it does.
    # each element added to the client bot is a dict with the key as a channel id and the value as the specific thing,
    # so that the bot can be played concurrently in multiple channels or servers (channel ids are unique globally)

    @commands.command()
    async def playoc(self, ctx):
        await ctx.send(f'Hi! Welcome to Only Connect. '
                       f'Type p for a practice round, or g '
                       f'for a full game. (full game mode not yet available)')
        self.client.games[ctx.channel.id] = "s"

    @commands.command()
    async def p(self, ctx):
        if self.client.games[ctx.channel.id] == "s":
            await ctx.send(f'Write the number of the Only Connect Round you would like to try:\
                        \n1 for connections, 2 for sequences, 3 for connecting wall and 4 for missing vowels.')
            self.client.games[ctx.channel.id] = "p"

    @commands.command(name="1")
    async def r1start(self, ctx):
        if self.client.games[ctx.channel.id] == "p":
            self.client.games[ctx.channel.id] = "p1"
            self.client.commandedkeys[ctx.channel.id] = "1"
            await OCresponses.ocresponses.readoutquestion(client=self.client, ctx=ctx, roundno = "1")
            #info = await OCresponsemethods.round1or2question(self, ctx=ctx)

    @commands.command(name="2")
    async def r2start(self, ctx):
        if self.client.games[ctx.channel.id] == "p":
            self.client.games[ctx.channel.id] = "p2"
            self.client.commandedkeys[ctx.channel.id] = "2"
            await OCresponses.ocresponses.readoutquestion(client=self.client, ctx=ctx, roundno = "2")

    @commands.command(name="3")
    async def r3start(self, ctx):
        self.client.commandedkeys[ctx.channel.id] = "3"
        self.client.games[ctx.channel.id] = "p3a"
        await OCresponses.ocresponses.readoutquestion(client=self.client, ctx=ctx, roundno="3")

    @commands.command(name="4")
    async def r4start(self, ctx):
        self.client.commandedkeys[ctx.channel.id] = "4"
        self.client.games[ctx.channel.id] = "p4"
        await OCresponses.ocresponses.readoutquestion(client=self.client, ctx=ctx, roundno="4")

    @commands.command(name="n")
    async def nextclue(self, ctx):
        if self.client.games[ctx.channel.id] in {"p1", "p2"}:  # or if an actual game
            self.client.commandedkeys[ctx.channel.id] = "n"
            info = await OCresponses.ocresponses.round1or2question(client=self.client, ctx=ctx)
        elif self.client.games[ctx.channel.id] in ("p3a"):
            self.client.commandedkeys[ctx.channel.id] = "n"
            await ctx.send(self.client.questionsinplay[ctx.channel.id].questioninfo["wallimages"][0])
            self.client.commandedkeys[ctx.channel.id] = "nulla"
            r3atimertask = asyncio.create_task(
                OCresponses.ocresponses.counttimefrommsg(client=self.client, channelid=ctx.channel.id, timelimit=60,
                                                         message=ctx.message))  # start the clock
            # note: when creating a timer task you don't await the method of the task inside
            # the create task method. if you do this will lead to a type error where asyncio expects a coroutine instead
            # of None
            self.client.timertasks[
                ctx.channel.id] = r3atimertask  # add timer to bot's timer dict for reference in other methods
            self.client.istimeron[ctx.channel.id] = True  # state in the bot's boolean dict that the timer is on

        elif self.client.games[ctx.channel.id] in ("p4") and (self.client.commandedkeys[ctx.channel.id] != "n" and self.client.commandedkeys[ctx.channel.id] != "nulla"):
            self.client.commandedkeys[ctx.channel.id] = "n"
            await OCresponses.ocresponses.round4question(client=self.client, message=ctx.message)



    @commands.Cog.listener()
    # checks for the right answer to a question in a message
    async def on_message(self,
                         message):  # make sure to include message in the argument, since it's a parameter of the on_message method
        if message.author == self.client.user:
            return
        # returning a correct answer in round 1 or 2
        elif self.client.games[message.channel.id] in {"p1", "p2"}:
            await OCresponses.ocresponses.round1or2response(client=self.client, message=message)

        #finding connections on a wall
        elif self.client.games[message.channel.id] in {"p3a"}:
            await OCresponses.ocresponses.round3aresponse(client=self.client, message=message)

        #guessing connections of wall groups
        elif self.client.games[message.channel.id] in {"p3b1"}:
            await OCresponses.ocresponses.round3banswercheck(client=self.client, message=message, currentsubround=1)
        elif self.client.games[message.channel.id] in {"p3b2"}:
            await OCresponses.ocresponses.round3banswercheck(client=self.client, message=message, currentsubround=2)
        elif self.client.games[message.channel.id] in {"p3b3"}:
            await OCresponses.ocresponses.round3banswercheck(client=self.client, message=message, currentsubround=3)
        elif self.client.games[message.channel.id] in {"p3b4"}:
            await OCresponses.ocresponses.round3banswercheck(client=self.client, message=message, currentsubround=4)

        #guessing missing vowels
        elif self.client.games[message.channel.id] in {"p4"} and len(message.content) > 1 and self.client.commandedkeys[message.channel.id] == "nulla":
            await OCresponses.ocresponses.round4answercheck(client=self.client, message=message)

            # events
    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self.client.user} has connected to Discord!')

async def setup(client: commands.Bot):
    await client.add_cog(OCmaincog(client))

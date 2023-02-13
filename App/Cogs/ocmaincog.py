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
                       f'for a full game.')
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

    @commands.command(name="n")
    async def nextclue(self, ctx):
        if self.client.games[ctx.channel.id] in ("p1", "p2"):  # or if an actual game
            self.client.commandedkeys[ctx.channel.id] = "n"
            info = await OCresponses.ocresponses.round1or2question(client=self.client, ctx=ctx)


    @commands.Cog.listener()
    # checks for the right answer to a question in a message
    async def on_message(self,
                         message):  # make sure to include message in the argument, since it's a parameter of the on_message method
        if message.author == self.client.user:
            return

        # returning a correct answer in round 1 or 2
        elif any(x in message.content.lower() for x in
                 self.client.questionsinplay[message.channel.id].questioninfo["answerlist"]) \
                and self.client.games[message.channel.id] in {"p1", "p2"} \
                and self.client.commandedkeys[message.channel.id] == "n":
            self.client.timertasks[message.channel.id].cancel()
            self.client.istimeron[message.channel.id] = False
            print("stopped the timer")
            # use dict method to return none if value not present. explicitly specifying content just in case error might show up
            if self.client.questionsinplay[message.channel.id].questioninfo["novelty"] == "audio":
                message.guild.voice_client.stop()
                await message.guild.voice_client.disconnect()
            if self.client.questionsinplay[message.channel.id].cluesgiven == 1:
                await message.channel.send("Correct with only 1 clue: that's 5 points!")
            elif self.client.questionsinplay[message.channel.id].cluesgiven == 2:
                await message.channel.send("Correct with only 2 clues: that's 3 points!")
            elif self.client.questionsinplay[message.channel.id].cluesgiven == 3:
                await message.channel.send("Correct with only 3 clues: that's 2 points!")
            elif self.client.questionsinplay[message.channel.id].cluesgiven == 4:
                await message.channel.send("Correct with 4 clues: that's 1 point!")
            await message.channel.send(self.client.questionsinplay[message.channel.id].questioninfo["response"])

            if self.client.games[message.channel.id] in {"p1", "p2"}:
                await message.channel.send("Thanks for playing! Type playoc to try another question.")
                self.client.games[message.channel.id] = "s"

        # returning an incorrect answer in round 1 or 2
        elif any(x in message.content.lower() for x in
                 self.client.questionsinplay[message.channel.id].questioninfo["answerlist"]) is False \
                and message.content != "n" \
                and (self.client.games[message.channel.id] in {"p1", "p2"}) \
                and self.client.commandedkeys[message.channel.id] == "n":
            self.client.timertasks[message.channel.id].cancel()
            self.client.istimeron[message.channel.id] = False
            print("stopped the timer")
            if self.client.questionsinplay[message.channel.id].questioninfo["novelty"] == "audio":
                message.guild.voice_client.stop()
                await message.guild.voice_client.disconnect()
            await message.channel.send("Not the right answer I'm afraid.")
            await message.channel.send(self.client.questionsinplay[message.channel.id].questioninfo["response"])
            if self.client.games[message.channel.id] in {"p1", "p2"}:
                await message.channel.send("Thanks for playing! Type playoc to try another question.")
                self.client.games[message.channel.id] = "s"

        # if self.client.games[ctx.channel.id] == "p1":  # or if an actual game
        #     self.client.commandedkeys[ctx.channel.id] = "n"
        #     info = await self.round1question(ctx=ctx)
        # elif self.client.games[ctx.channel.id] == "p2":
        #     pass

    # events
    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self.client.user} has connected to Discord!')

async def setup(client: commands.Bot):
    await client.add_cog(OCmaincog(client))

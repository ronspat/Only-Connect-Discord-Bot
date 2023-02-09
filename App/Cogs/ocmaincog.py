import Questions.questions
import discord
from discord.ext import commands
from OCresponses.ocresponses import OCresponsemethods

#for creating a timer
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
#each element added to the client bot is a dict with the key as a channel id and the value as the specific thing,
#so that the bot can be played concurrently in multiple channels or servers (channel ids are unique globally)

    async def counttime(self, channelid, timelimit, ctx: discord.ext.commands.Context):
        await asyncio.sleep(timelimit)
        self.client.istimeron[channelid] = False
        #print("Task finished")
        await ctx.send('Sorry you ran out of time!')
        await ctx.send(self.client.questionsinplay[ctx.channel.id].questioninfo["response"])
        #The timer is started by using it to construct an Asyncio task object
        #with the create task method in asyncio.
        # a specific task.cancel() method is used in methods where the timer is stopped early.
        # If the timer is not stopped early, the code here will continue running beyond the asyncio sleep method
        if self.client.questionsinplay[ctx.channel.id].questioninfo["novelty"] == "audio":
            ctx.guild.voice_client.stop()
            await ctx.guild.voice_client.disconnect()

        if self.client.games[ctx.channel.id] in {"p1", "p2"}:
            await ctx.channel.send("Thanks for playing! Type playoc to try another question.")
            self.client.games[ctx.channel.id] = "s"

    #question methods

    async def round1question(self, ctx: commands.Context, question: Questions.questions.Question = None, questionid: str = None):

        if self.client.games[ctx.channel.id] == "p1" or self.client.games[ctx.channel.id] == "g1":

            if self.client.commandedkeys[ctx.channel.id] == "1":

                questionlist = Questions.questions.\
                                getquestionlist("https://onlyconnect.s3.eu-west-2.amazonaws.com/Questions/r1.txt")
                questioninfodict = Questions.questions.getquestion(questionlist, number=None) # gets a random round 1 question
                self.client.questionsinplay[ctx.channel.id] = Questions.questions.Question(questioninfo=questioninfodict)
                self.client.questionsinplay[ctx.channel.id].stage = "started"

                if self.client.questionsinplay[ctx.channel.id].questioninfo["novelty"] == "no":
                    await ctx.send('What is the connection between these clues. '
                      'Press n to get your first clue and start the timer (40 seconds), and n again for every additional clue. '
                      'Type out your answer whenever you think you know the connection.')
                elif self.client.questionsinplay[ctx.channel.id].questioninfo["novelty"] == "picture":
                    await ctx.send('These are going to be PICTURE clues... what is the connection between them. '
                                   'Press n to see your first clue and start the timer (40 seconds), and n again for every additional clue.'
                                   'Type out your answer whenever you think you know the connection.')
                elif self.client.questionsinplay[ctx.channel.id].questioninfo["novelty"] == "audio":
                    await ctx.send("Aah, it's a MUSIC question! You'll be hearing your clues, what is the connection betweeen them. "
                                   'Press n to hear your first clue and start the timer (40 seconds), and n again for every additional clue. '
                                   'Make sure you are in an audio channel that I have access to join before starting. '
                                   'Type out your answer whenever you think you know the connection.')

            #1st clue
            elif self.client.commandedkeys[ctx.channel.id] == "n" \
                    and self.client.questionsinplay[ctx.channel.id].stage == "started" \
                    and self.client.questionsinplay[ctx.channel.id].cluesgiven == 0:
                starttimer = True
                if self.client.questionsinplay[ctx.channel.id].questioninfo["novelty"] in {"no", "picture", "naudio"}:
                    await ctx.send(self.client.questionsinplay[ctx.channel.id].questioninfo["clues"][0])
                elif self.client.questionsinplay[ctx.channel.id].questioninfo["novelty"] == "audio":
                    livechannels = [c.channel for c in self.client.voice_clients]
                    if ctx.guild.voice_client is not None and ctx.author.voice.channel not in livechannels: #if the bot is already playing music in another channel
                        print(ctx.author.voice.channel)
                        print(livechannels)
                        await ctx.send(
                            "I'm already playing music in this server for another question. Once I've left that voice chat,"
                            " press n to start your music question.") # n.b. the code for the bot leaving a vc happens at the end of a question
                        starttimer = False
                    elif ctx.author.voice is not None and ctx.author.voice.channel not in livechannels:
                        #voice clients represent voice channel of each server the bot is in
                        # connecting to a voice channel returns a voice client. Here it's checking if the user's VC is not one the bot is in
                        try:
                            voiceclient = await ctx.author.voice.channel.connect()
                        except:
                            await ctx.send("I can't connect to the voice channel you are in! Try another in the server and then click n again when ready.")
                            starttimer = False
                        else:
                            voiceclient.play(discord.FFmpegPCMAudio(self.client.questionsinplay[ctx.channel.id].questioninfo["clues"][0]))
                            #note that play and stop are not an awaitable method
                    if ctx.author.voice is None:
                        await ctx.send("Please connect to a voice channel first! Click n when you are ready.")
                        starttimer = False
                if starttimer is True:
                    self.client.questionsinplay[ctx.channel.id].cluesgiven = 1
                    #start timer
                    r1timertask = asyncio.create_task(self.counttime(channelid=ctx.channel.id,timelimit=20, ctx=ctx))# start the clock
                    self.client.timertasks[ctx.channel.id] = r1timertask # add timer to bot's timer dict for reference in other methods
                    self.client.istimeron[ctx.channel.id] = True # state in the bot's boolean dict that the timer is on

            #2nd clue
            elif self.client.commandedkeys[ctx.channel.id] == "n"\
                    and self.client.questionsinplay[ctx.channel.id].stage == "started"\
                    and self.client.questionsinplay[ctx.channel.id].cluesgiven == 1\
                    and self.client.istimeron[ctx.channel.id] is True:

                if self.client.questionsinplay[ctx.channel.id].questioninfo["novelty"] in {"no", "picture"}:
                    await ctx.send(self.client.questionsinplay[ctx.channel.id].questioninfo["clues"][1])
                elif self.client.questionsinplay[ctx.channel.id].questioninfo["novelty"] == "audio":
                    for vc in self.client.voice_clients:
                        if vc.guild == ctx.guild:
                            vc.guild.voice_client.stop()
                            vc.guild.voice_client.play(discord.FFmpegPCMAudio(self.client.questionsinplay[ctx.channel.id].questioninfo["clues"][1]))
                        #need to stop the old song playing first, additionally the voice client
                        # object must be the one created that can be called from the bot's list, not from the
                        # guild of the context
                self.client.questionsinplay[ctx.channel.id].cluesgiven = 2

            #3rd clue
            elif self.client.commandedkeys[ctx.channel.id] == "n"\
                    and self.client.questionsinplay[ctx.channel.id].stage == "started"\
                    and self.client.questionsinplay[ctx.channel.id].cluesgiven == 2\
                    and self.client.istimeron[ctx.channel.id] is True:

                if self.client.questionsinplay[ctx.channel.id].questioninfo["novelty"] in {"no", "picture"}:
                    await ctx.send(self.client.questionsinplay[ctx.channel.id].questioninfo["clues"][2])
                elif self.client.questionsinplay[ctx.channel.id].questioninfo["novelty"] == "audio":
                    for vc in self.client.voice_clients:
                        if vc.guild == ctx.guild:
                            vc.guild.voice_client.stop()
                            vc.guild.voice_client.play(discord.FFmpegPCMAudio(
                                self.client.questionsinplay[ctx.channel.id].questioninfo["clues"][2]))
                self.client.questionsinplay[ctx.channel.id].cluesgiven = 3

            #4th clue
            elif self.client.commandedkeys[ctx.channel.id] == "n"\
                    and self.client.questionsinplay[ctx.channel.id].stage == "started"\
                    and self.client.questionsinplay[ctx.channel.id].cluesgiven == 3\
                    and self.client.istimeron[ctx.channel.id] is True:

                if self.client.questionsinplay[ctx.channel.id].questioninfo["novelty"] in {"no", "picture"}:
                    await ctx.send(self.client.questionsinplay[ctx.channel.id].questioninfo["clues"][3])
                elif self.client.questionsinplay[ctx.channel.id].questioninfo["novelty"] == "audio":
                    for vc in self.client.voice_clients:
                        if vc.guild == ctx.guild:
                            vc.guild.voice_client.stop()
                            vc.guild.voice_client.play(discord.FFmpegPCMAudio(
                                self.client.questionsinplay[ctx.channel.id].questioninfo["clues"][3]))
                self.client.questionsinplay[ctx.channel.id].cluesgiven = 4

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
            info = await self.round1question(ctx=ctx)

    # @commands.command(name="2")
    # async def r2start(self, ctx):
    #     if self.client.games[ctx.channel.id] == "p":
    #         self.client.games[ctx.channel.id] = "p2"
    #         self.client.commandedkeys[ctx.channel.id] = "2"
    #         info = await self.round2question(ctx=ctx)

    @commands.command(name="n")
    async def nextclue(self, ctx):
        if self.client.games[ctx.channel.id] == "p1": #or if an actual game
            self.client.commandedkeys[ctx.channel.id] = "n"
            info = await self.round1question(ctx=ctx)
        elif self.client.games[ctx.channel.id] == "p2":
            pass

    @commands.Cog.listener()
    #checks for the right answer to a question in a message
    async def on_message(self, message): #make sure to include message in the argument, since it's a parameter of the on_message method
        if message.author == self.client.user:
            return

        #returning a correct answer in round 1 or 2
        elif any(x in message.content.lower() for x in self.client.questionsinplay[message.channel.id].questioninfo["answerlist"]) \
                and self.client.games[message.channel.id] in {"p1", "p2"} \
                and self.client.commandedkeys[message.channel.id] == "n":
            self.client.timertasks[message.channel.id].cancel()
            self.client.istimeron = False
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
        elif any(x in message.content.lower() for x in self.client.questionsinplay[message.channel.id].questioninfo["answerlist"]) is False \
                and message.content != "n"\
                and (self.client.games[message.channel.id] in {"p1", "p2"})\
                and self.client.commandedkeys[message.channel.id] == "n":
            self.client.timertasks[message.channel.id].cancel()
            self.client.istimeron = False
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


    #events
    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self.client.user} has connected to Discord!')


async def setup(client: commands.Bot):
    await client.add_cog(OCmaincog(client))


import Questions.questions
import asyncio
from discord.ext import commands


class OCmaincog(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.client.games = {}
        self.client.questionsinplay = {}
        self.client.commandedkeys = {}
        self.client.timertasks = {}
        self.client.istimeron = {}
# the client is a Bot object class. I am not sure why it allows you to add new variables to the bot object but it does.
#each element added to the client bot is a dict with the key as a channel id and the value as the specific thing,
#so that the bot can be played concurrently in multiple channels or servers (channel ids are unique globally)

    #timer method
    async def counttime(self, channelid, timelimit, ctx: commands.Context):
        await asyncio.sleep(timelimit)
        self.client.istimeron[channelid] = False
        print("Task finished")
        await ctx.send('Sorry you ran out of time!')
        #The timer is started by using it to construct an Asyncio task object
        #with the create task method in asyncio.
        # a specific task.cancel() method is used in methods where the timer is stopped early.
        # If the timer is not stopped early, the code here will continue running beyond the asyncio sleep method

    #question methods

    async def round1question(self, ctx: commands.Context, question: Questions.questions.Question = None, questionid: str = None):
        print(ctx.channel.id)

        if self.client.games[ctx.channel.id] == "p1" or self.client.games[ctx.channel.id] == "g1":

            if self.client.commandedkeys[ctx.channel.id] == "1":

                questionlist = Questions.questions.\
                                getquestionlist("https://onlyconnect.s3.eu-west-2.amazonaws.com/Questions/r1.txt")
                questioninfodict = Questions.questions.getquestion(questionlist) # gets a random round 1 question
                self.client.questionsinplay[ctx.channel.id] = Questions.questions.Question(questioninfo=questioninfodict)
                self.client.questionsinplay[ctx.channel.id].stage = "started"

                await ctx.send('I want to know what is the connection between these clues. '
                      'Press n to get your first clue and start the timer (40 seconds), and n again for every additional clue.'
                      'Type out your answer whenever you think you know the connection.')
            elif self.client.commandedkeys[ctx.channel.id] == "n" \
                    and self.client.questionsinplay[ctx.channel.id].stage == "started" \
                    and self.client.questionsinplay[ctx.channel.id].cluesgiven == 0:
                await ctx.send('First Clue')
                self.client.questionsinplay[ctx.channel.id].cluesgiven = 1

                #start timer
                r1timertask = asyncio.create_task(self.counttime(channelid=ctx.channel.id,timelimit=5, ctx=ctx)) # start the clock
                self.client.timertasks[ctx.channel.id] = r1timertask # add timer to bot's timer dict for reference in other methods
                self.client.istimeron[ctx.channel.id] = True # state in the bot's boolean dict that the timer is on
            elif self.client.commandedkeys[ctx.channel.id] == "n"\
                    and self.client.questionsinplay[ctx.channel.id].stage == "started"\
                    and self.client.questionsinplay[ctx.channel.id].cluesgiven == 1\
                    and self.client.istimeron[ctx.channel.id] is True:
                await ctx.send('2nd Clue')
                self.client.questionsinplay[ctx.channel.id].cluesgiven = 2
            elif self.client.commandedkeys[ctx.channel.id] == "n"\
                    and self.client.questionsinplay[ctx.channel.id].stage == "started"\
                    and self.client.questionsinplay[ctx.channel.id].cluesgiven == 2\
                    and self.client.istimeron[ctx.channel.id] is True:
                await ctx.send('3rd Clue')
                self.client.questionsinplay[ctx.channel.id].cluesgiven = 3
            elif self.client.commandedkeys[ctx.channel.id] == "n"\
                    and self.client.questionsinplay[ctx.channel.id].stage == "started"\
                    and self.client.questionsinplay[ctx.channel.id].cluesgiven == 3\
                    and self.client.istimeron[ctx.channel.id] is True:
                await ctx.send('4th Clue')
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
        elif message.content.startswith('nehek'):
            self.client.timertasks[message.channel.id].cancel()
            self.client.istimeron = False
            print("stopped the timer")
            await message.channel.send(content=self.client.games.get(message.channel.id)) #use dict method to return none if value not present

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


import Questions.questions
from discord.ext import commands


class OCmaincog(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.client.games = {}
        self.client.questionsinplay = {}
        self.client.commandedkeys = {}
# the client is a Bot object class

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
                #await timer = None
            elif self.client.commandedkeys[ctx.channel.id] == "n"\
                    and self.client.questionsinplay[ctx.channel.id].stage == "started"\
                    and self.client.questionsinplay[ctx.channel.id].cluesgiven == 1:
                await ctx.send('2nd Clue')
                self.client.questionsinplay[ctx.channel.id].cluesgiven = 2
            elif self.client.commandedkeys[ctx.channel.id] == "n"\
                    and self.client.questionsinplay[ctx.channel.id].stage == "started"\
                    and self.client.questionsinplay[ctx.channel.id].cluesgiven == 2:
                await ctx.send('3rd Clue')
                self.client.questionsinplay[ctx.channel.id].cluesgiven = 3
            elif self.client.commandedkeys[ctx.channel.id] == "n"\
                    and self.client.questionsinplay[ctx.channel.id].stage == "started"\
                    and self.client.questionsinplay[ctx.channel.id].cluesgiven == 3:
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



    #events
    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self.client.user} has connected to Discord!')


async def setup(client: commands.Bot):
    await client.add_cog(OCmaincog(client))


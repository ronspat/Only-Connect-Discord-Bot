import Questions.questions
from discord.ext import commands


class OCmaincog(commands.Cog):

    def __init__(self, client):
        self.client = client

    #question methods

    # async def round1question(self, ctx: commands.Context, question: Questions.questions.Question):
    #     global q1status
    #     q1status = "started"
    #     question.stage = "started"
    #     await ctx.send('I want to know what is the connection between these clues. '\
    #              'Press n to get your first clue and start the timer (40 seconds), and n again for every additional clue.'\
    #              'Type out your answer whenever you think you know the connection.')
    #
    # @commands.command()
    # async def playoc(self, ctx):
    #     await ctx.send(f'Hi! Welcome to Only Connect. '
    #                    f'Type .p for a practice round, or .g '
    #                    f'for a full game.')

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


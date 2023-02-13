import asyncio
import discord
import Questions.questions
from discord.ext import commands


# timer method
async def counttime(client: commands.Bot, channelid, timelimit, ctx: commands.Context):
    await asyncio.sleep(timelimit)
    client.istimeron[channelid] = False
    # print("Task finished")
    await ctx.send('Sorry you ran out of time!')
    await ctx.send(client.questionsinplay[ctx.channel.id].questioninfo["response"])
    # The timer is started by using it to construct an Asyncio task object
    # with the create task method in asyncio.
    # a specific task.cancel() method is used in methods where the timer is stopped early.
    # If the timer is not stopped early, the code here will continue running beyond the asyncio sleep method
    if client.questionsinplay[ctx.channel.id].questioninfo["novelty"] == "audio":
        ctx.guild.voice_client.stop()
        await ctx.guild.voice_client.disconnect()

    if client.games[ctx.channel.id] in {"p1", "p2"}:
        await ctx.channel.send("Thanks for playing! Type playoc to try another question.")
        client.games[ctx.channel.id] = "s"


async def readoutquestion(client: commands.Bot, ctx: commands.Context, roundno: str,
                          question: Questions.questions.Question = None, questionid: str = None):
    questionlist = Questions.questions. \
        getquestionlist("https://onlyconnect.s3.eu-west-2.amazonaws.com/Questions/r" + roundno + ".txt")

    if "p" in client.games[ctx.channel.id]:
        questioninfodict = Questions.questions.getquestion(questionlist, number=None)  # number=None gets a random question

    client.questionsinplay[ctx.channel.id] = Questions.questions.Question(questioninfo=questioninfodict)
    client.questionsinplay[ctx.channel.id].stage = "started"

    if client.commandedkeys[ctx.channel.id] == "1":
        if client.questionsinplay[ctx.channel.id].questioninfo["novelty"] == "no":
            await ctx.send('What is the connection between these clues. '
                           'Press n to get your first clue and start the timer (40 seconds), and n again for every additional clue. '
                           'Type out your answer whenever you think you know the connection.')
        elif client.questionsinplay[ctx.channel.id].questioninfo["novelty"] == "picture":
            await ctx.send('These are going to be PICTURE clues... what is the connection between them. '
                           'Press n to see your first clue and start the timer (40 seconds), and n again for every additional clue.'
                           'Type out your answer whenever you think you know the connection.')
        elif client.questionsinplay[ctx.channel.id].questioninfo["novelty"] == "audio":
            await ctx.send(
                "Aah, it's a MUSIC question! You'll be hearing your clues, what is the connection betweeen them. "
                'Press n to hear your first clue and start the timer (40 seconds), and n again for every additional clue. '
                'Make sure you are in an audio channel that I have access to join before starting. '
                'Type out your answer whenever you think you know the connection.')

    elif client.commandedkeys[ctx.channel.id] == "2":
        if client.questionsinplay[ctx.channel.id].questioninfo["novelty"] == "no":
            await ctx.send('What comes fourth in this sequence. '
                           'Press n to get your first clue and start the timer (40 seconds), and n again for every additional clue. '
                           'Type out your answer whenever you think you know the connection.')
        elif client.questionsinplay[ctx.channel.id].questioninfo["novelty"] == "picture":
            await ctx.send('What comes fourth in this PICTURE sequence? '
                           'Press n to see your first clue and start the timer (40 seconds), and n again for every additional clue.'
                           'Type out your answer whenever you think you know the connection.')
        elif client.questionsinplay[ctx.channel.id].questioninfo["novelty"] == "audio":
            await ctx.send("It's a lovely MUSIC sequence! "
                           'Press n to hear your first clue and start the timer (40 seconds), and n again for every additional clue. '
                           'Make sure you are in an audio channel that I have access to join before starting. '
                           'Type out your answer whenever you think you know the connection.')


async def round1or2question(client: commands.Bot, ctx: commands.Context):
    if client.games[ctx.channel.id] in ("p1", "p2", "g1", "g2"):

        # 1st clue
        if client.commandedkeys[ctx.channel.id] == "n" \
                and client.questionsinplay[ctx.channel.id].stage == "started" \
                and client.questionsinplay[ctx.channel.id].cluesgiven == 0:
            starttimer = True
            if client.questionsinplay[ctx.channel.id].questioninfo["novelty"] in {"no", "picture", "naudio"}:
                await ctx.send(client.questionsinplay[ctx.channel.id].questioninfo["clues"][0])
            elif client.questionsinplay[ctx.channel.id].questioninfo["novelty"] == "audio":
                livechannels = [c.channel for c in client.voice_clients]
                if ctx.guild.voice_client is not None and ctx.author.voice.channel not in livechannels:  # if the bot is already playing music in another channel
                    print(ctx.author.voice.channel)
                    print(livechannels)
                    await ctx.send(
                        "I'm already playing music in this server for another question. Once I've left that voice chat,"
                        " press n to start your music question.")  # n.b. the code for the bot leaving a vc happens at the end of a question
                    starttimer = False
                elif ctx.author.voice is not None and ctx.author.voice.channel not in livechannels:
                    # voice clients represent voice channel of each server the bot is in
                    # connecting to a voice channel returns a voice client. Here it's checking if the user's VC is not one the bot is in
                    try:
                        voiceclient = await ctx.author.voice.channel.connect()
                    except:
                        await ctx.send(
                            "I can't connect to the voice channel you are in! Try another in the server and then click n again when ready.")
                        starttimer = False
                    else:
                        voiceclient.play(discord.FFmpegPCMAudio(
                            client.questionsinplay[ctx.channel.id].questioninfo["clues"][0]))
                        # note that play and stop are not an awaitable method
                if ctx.author.voice is None:
                    await ctx.send("Please connect to a voice channel first! Click n when you are ready.")
                    starttimer = False
            if starttimer is True:
                client.questionsinplay[ctx.channel.id].cluesgiven = 1
                # start timer
                r1timertask = asyncio.create_task(
                    counttime(client=client, channelid=ctx.channel.id, timelimit=20, ctx=ctx))  # start the clock
                client.timertasks[
                    ctx.channel.id] = r1timertask  # add timer to bot's timer dict for reference in other methods
                client.istimeron[ctx.channel.id] = True  # state in the bot's boolean dict that the timer is on

        # 2nd clue
        elif client.commandedkeys[ctx.channel.id] == "n" \
                and client.questionsinplay[ctx.channel.id].stage == "started" \
                and client.questionsinplay[ctx.channel.id].cluesgiven == 1 \
                and client.istimeron[ctx.channel.id] is True:
            print(client.istimeron)
            if client.questionsinplay[ctx.channel.id].questioninfo["novelty"] in {"no", "picture"}:
                await ctx.send(client.questionsinplay[ctx.channel.id].questioninfo["clues"][1])
            elif client.questionsinplay[ctx.channel.id].questioninfo["novelty"] == "audio":
                for vc in client.voice_clients:
                    if vc.guild == ctx.guild:
                        vc.guild.voice_client.stop()
                        vc.guild.voice_client.play(discord.FFmpegPCMAudio(
                            client.questionsinplay[ctx.channel.id].questioninfo["clues"][1]))
                    # need to stop the old song playing first, additionally the voice client
                    # object must be the one created that can be called from the bot's list, not from the
                    # guild of the context
            client.questionsinplay[ctx.channel.id].cluesgiven = 2

        # 3rd clue
        elif client.commandedkeys[ctx.channel.id] == "n" \
                and client.questionsinplay[ctx.channel.id].stage == "started" \
                and client.questionsinplay[ctx.channel.id].cluesgiven == 2 \
                and client.istimeron[ctx.channel.id] is True:

            if client.questionsinplay[ctx.channel.id].questioninfo["novelty"] in {"no", "picture"}:
                await ctx.send(client.questionsinplay[ctx.channel.id].questioninfo["clues"][2])
            elif client.questionsinplay[ctx.channel.id].questioninfo["novelty"] == "audio":
                for vc in client.voice_clients:
                    if vc.guild == ctx.guild:
                        vc.guild.voice_client.stop()
                        vc.guild.voice_client.play(discord.FFmpegPCMAudio(
                            client.questionsinplay[ctx.channel.id].questioninfo["clues"][2]))
            client.questionsinplay[ctx.channel.id].cluesgiven = 3

        # 4th clue (round 1 only)
        elif client.commandedkeys[ctx.channel.id] == "n" \
                and client.questionsinplay[ctx.channel.id].stage == "started" \
                and client.questionsinplay[ctx.channel.id].cluesgiven == 3 \
                and client.istimeron[ctx.channel.id] is True \
                and client.games[ctx.channel.id] in ("p1", "g1"):

            if client.questionsinplay[ctx.channel.id].questioninfo["novelty"] in {"no", "picture"}:
                await ctx.send(client.questionsinplay[ctx.channel.id].questioninfo["clues"][3])
            elif client.questionsinplay[ctx.channel.id].questioninfo["novelty"] == "audio":
                for vc in client.voice_clients:
                    if vc.guild == ctx.guild:
                        vc.guild.voice_client.stop()
                        vc.guild.voice_client.play(discord.FFmpegPCMAudio(
                            client.questionsinplay[ctx.channel.id].questioninfo["clues"][3]))
            client.questionsinplay[ctx.channel.id].cluesgiven = 4

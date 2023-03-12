import asyncio
import operator

import discord
import Questions.questions
from discord.ext import commands


# timer method
async def counttime(client: commands.Bot, channelid, timelimit, ctx: commands.Context):
    #used for r1 or 2 timers
    await asyncio.sleep(timelimit)
    client.istimeron[channelid] = False
    # print("Task finished")
    # The timer is started by using it to construct an Asyncio task object
    # with the create task method in asyncio.
    # a specific task.cancel() method is used in methods where the timer is stopped early.
    # If the timer is not stopped early, the code here will continue running beyond the asyncio sleep method

    if client.games[ctx.channel.id] in {"p1", "p2"}:
        if client.questionsinplay[ctx.channel.id].questioninfo["novelty"] == "audio":
            print("it is an audio question, stopping song and connection")
            ctx.guild.voice_client.stop()
            await ctx.guild.voice_client.disconnect()
        await ctx.send('Sorry you ran out of time!')
        await ctx.send(client.questionsinplay[ctx.channel.id].questioninfo["response"])
        await ctx.channel.send("Thanks for playing! Type playoc to try another question.")
        client.games[ctx.channel.id] = "s"

async def round3btimer(client: commands.Bot, message: discord.Message, startercluegroupno: int):
    for groupno in range(startercluegroupno, 5):
        await message.channel.send(
            str(client.questionsinplay[message.channel.id].questioninfo["group " + str(groupno)]["items"]))
        client.istimeron[message.channel.id] = True
        await asyncio.sleep(10)
        client.istimeron[message.channel.id] = False
        await message.channel.send(
            str("Not quick enough. "+client.questionsinplay[message.channel.id].questioninfo["group " + str(groupno)]["response"]))
        if groupno < 4:
            client.games[message.channel.id] = "p3b"+str(startercluegroupno+1)
    client.games[message.channel.id] = "s"
    if client.questionsinplay[message.channel.id].wallpoints == 8:
        await message.channel.send(
            "You got 4 points for solving the wall, 4 points for the connections, plus a bonus 2 points!")
        client.questionsinplay[message.channel.id].wallpoints = 10
    await message.channel.send(
        "You got " + str(client.questionsinplay[message.channel.id].wallpoints) + " points in total.")
    await message.channel.send("That's the end of the round. Thanks for playing! Type playoc to try another question.")



async def counttimefrommsg(client: commands.Bot, channelid, timelimit, message: discord.Message):
    #used for round 3a or 4 timers
    await asyncio.sleep(timelimit)
    client.istimeron[channelid] = False
    if client.games[message.channel.id] in {"p3a"}:
        await message.channel.send('Sorry you ran out of time and the wall has frozen!')
        client.games[message.channel.id] = "p3b1"
        await message.channel.send(
            "Now see if you know the connections. You'll get 10 seconds to type the connection for each group, starting with:")
        r3btimertask = asyncio.create_task(
            round3btimer(client=client, message=message, startercluegroupno=1))  # start the clock
        client.timertasks[
            message.channel.id] = r3btimertask  # add timer to bot's timer dict for reference in other methods
        client.istimeron[message.channel.id] = True  # state in the bot's boolean dict that the timer is on
    if client.games[message.channel.id] in {"p4"}:
        client.games[message.channel.id] = "s"
        await message.channel.send('Sorry you ran out of time!')
        await message.channel.send("That's the end of the round. Thanks for playing! You scored "+ str(client.questionsinplay[message.channel.id].round4points)+" points. Type playoc to try another question.")


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
            await ctx.send("It's a MUSIC sequence! "
                           'Press n to hear your first clue and start the timer (40 seconds), and n again for every additional clue. '
                           'Make sure you are in an audio channel that I have access to join before starting. '
                           'Type out your answer whenever you think you know the connection.')

    elif client.commandedkeys[ctx.channel.id] == "3":
        await ctx.send('The connecting wall features 4 groups of 4 connected clues each, 16 clues in total. '
                       'The clues are jumbled up, and there may be more than 4 clues that'
                       'fit in one group, but there will be only one perfect solution.'
                       "Press n to get your wall and start the timer (2 mins 30 seconds). "
                       "Type out any 4 clues, and I'll let you know if they're a group. \nOnce you've got 3 groups, "
                       "you only get 3 tries to get the 4th group before the wall freezes.")

    elif client.commandedkeys[ctx.channel.id] == "4":
        await ctx.send('In this round the vowels will be taken out of famous names, phrases and sayings. '
                       'The consonants will be left with random spacing between or within the word(s). \n'
                       "Simply type the unscrambled clue with correct letters and spacing, but be careful"
                       "because one letter or space out of place counts as an incorrect answer and subtracts a point!\n Press n to start.")


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
                    # voice clients represent voice channel connections of each server the bot is in
                    # connecting to a voice channel returns a voice client. Here it's checking if the user's VC is not one the bot is in
                    try:
                        voiceclient = await ctx.author.voice.channel.connect()
                    except Exception as ex:
                        print(ex)
                        await ctx.send(
                            "I can't connect to the voice channel you are in! Try another in the server and then click n again when ready.")
                        starttimer = False
                    else:
                        print("succesfully connected to the voice channel!")
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
            if client.questionsinplay[ctx.channel.id].questioninfo["novelty"] in {"no", "picture"}:
                await ctx.send(client.questionsinplay[ctx.channel.id].questioninfo["clues"][1])
            elif client.questionsinplay[ctx.channel.id].questioninfo["novelty"] == "audio":
                print("audito question second clue requested")
                for vc in client.voice_clients:
                    if vc.guild == ctx.guild:
                        print("identified vc to stop")
                        vc.guild.voice_client.stop()
                        print("stopped audio")
                        print(str(vc))
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

async def round1or2response(client: commands.Bot, message: discord.Message):
    # returning a correct answer in round 1 or 2
    if any(x in message.content.lower() for x in
           client.questionsinplay[message.channel.id].questioninfo["answerlist"]) \
            and client.commandedkeys[message.channel.id] == "n":
        client.timertasks[message.channel.id].cancel()
        client.istimeron[message.channel.id] = False
        # use dict method to return none if value not present. explicitly specifying content just in case error might show up
        if client.questionsinplay[message.channel.id].questioninfo["novelty"] == "audio":
            message.guild.voice_client.stop()
            await message.guild.voice_client.disconnect()
        if client.questionsinplay[message.channel.id].cluesgiven == 1:
            await message.channel.send("Correct with only 1 clue: that's 5 points!")
        elif client.questionsinplay[message.channel.id].cluesgiven == 2:
            await message.channel.send("Correct with only 2 clues: that's 3 points!")
        elif client.questionsinplay[message.channel.id].cluesgiven == 3:
            await message.channel.send("Correct with only 3 clues: that's 2 points!")
        elif client.questionsinplay[message.channel.id].cluesgiven == 4:
            await message.channel.send("Correct with 4 clues: that's 1 point!")
        await message.channel.send(client.questionsinplay[message.channel.id].questioninfo["response"])

        if client.games[message.channel.id] in {"p1", "p2"}:
            await message.channel.send("Thanks for playing! Type playoc to try another question.")
            client.games[message.channel.id] = "s"
        return

    # returning an incorrect answer in round 1 or 2
    elif any(x in message.content.lower() for x in
             client.questionsinplay[message.channel.id].questioninfo["answerlist"]) is False \
            and message.content != "n" \
            and (client.games[message.channel.id] in {"p1", "p2"}) \
            and client.commandedkeys[message.channel.id] == "n":
        client.timertasks[message.channel.id].cancel()
        client.istimeron[message.channel.id] = False
        if client.questionsinplay[message.channel.id].questioninfo["novelty"] == "audio":
            message.guild.voice_client.stop()
            await message.guild.voice_client.disconnect()
        await message.channel.send("Not the right answer I'm afraid.")
        await message.channel.send(client.questionsinplay[message.channel.id].questioninfo["response"])
        if client.games[message.channel.id] in {"p1", "p2"}:
            await message.channel.send("Thanks for playing! Type playoc to try another question.")
            client.games[message.channel.id] = "s"
        return

async def round3aresponse(client: commands.Bot, message: discord.Message):
    groupmatched = None
    cluesmatcheddict = {}
    for groupno in range(1, 5):
        for groupitem in client.questionsinplay[message.channel.id].questioninfo["group " + str(groupno)]["items"]:
            if groupitem in message.content.lower():
                additemtomatchedcluesdict = True
                if cluesmatcheddict == {}:
                    additemtomatchedcluesdict = True
                else:
                    for matchedclue, matchedcluegroupno in cluesmatcheddict.items():
                        if matchedclue in groupitem and matchedcluegroupno != groupno and message.content.lower().count(
                                matchedclue) < 2:
                            cluesmatcheddict.pop(matchedclue)  # removes an groupitem if it's a subset of
                            # another groupitem from another group e.g. remove no if clue submitted was piano. This allows the bot not to
                            # double count an item whose string contains another item as a substring in it when checking later if there are too many items
                        elif groupitem in matchedclue and matchedcluegroupno != groupno and message.content.lower().count(
                                groupitem) < 2:
                            # e.g. if already matched "piano" and now matching "no", ignore "no"
                            additemtomatchedcluesdict = False
                        elif matchedclue in groupitem and matchedcluegroupno == groupno and message.content.lower().count(
                                matchedclue) < 2:
                            additemtomatchedcluesdict = False
                        # pass if one clue in a group is a substring of another but two separate versions of the substring are not detected
                        elif groupitem in matchedclue and matchedcluegroupno == groupno and message.content.lower().count(
                                groupitem) < 2:
                            additemtomatchedcluesdict = False
                        # pass if one clue in a group is a substring of another but two separate versions of the substring are not detected
                if additemtomatchedcluesdict == True:
                    cluesmatcheddict.update({groupitem: groupno})
        if len(cluesmatcheddict) == 4 and operator.countOf(cluesmatcheddict.values(),
                                                           groupno) == 4 and groupmatched is None:
            groupmatched = "group " + str(groupno)
        elif len(cluesmatcheddict) > 4:
            await message.channel.send("There are too many clues in this group. Please try again")
            groupmatched = None
            break

    if groupmatched is None and operator.countOf(client.questionsinplay[message.channel.id].groupsfound.values(),
                                                 True) == 2:
        if client.questionsinplay[message.channel.id].round3lives == 3:
            client.questionsinplay[message.channel.id].round3lives = 2
            await message.channel.send("Not a match. You have 2 lives left")
        elif client.questionsinplay[message.channel.id].round3lives == 2:
            client.questionsinplay[message.channel.id].round3lives = 1
            await message.channel.send("Not a match. You have 1 life left")
        elif client.questionsinplay[message.channel.id].round3lives == 1: #run out of wall lives
            client.questionsinplay[message.channel.id].round3lives = 0
            await message.channel.send("You're out of lives and the wall has frozen.")
            if client.games[message.channel.id] in {"p3a"}:
                client.games[message.channel.id] = "p3b1"
                client.timertasks[message.channel.id].cancel()
                client.istimeron[message.channel.id] = False
                await message.channel.send(
                    "Now see if you know the connections. You'll get 5 seconds to type the connection for each group, starting with:")
                r3btimertask = asyncio.create_task(
                    round3btimer(client=client, startercluegroupno=1,
                                                             message=message))  # start the clock
                client.timertasks[
                    message.channel.id] = r3btimertask  # add timer to bot's timer dict for reference in other methods
                client.istimeron[message.channel.id] = True  # state in the bot's boolean dict that the timer is on

    if groupmatched is not None:
        if client.questionsinplay[message.channel.id].groupsfound[groupmatched] == False:
            await message.channel.send("You got a new group!:\n" + str(
                client.questionsinplay[message.channel.id].questioninfo[groupmatched]["items"])+"\nThat's 1 point.")
            client.questionsinplay[message.channel.id].groupsfound[groupmatched] = True
            client.questionsinplay[message.channel.id].wallpoints += 1
        if operator.countOf(client.questionsinplay[message.channel.id].groupsfound.values(), True) == 3:
            await message.channel.send("Congratulations! You solved the wall.")
            client.questionsinplay[message.channel.id].wallpoints += 1
            if client.games[message.channel.id] in {"p3a"}:
                client.games[message.channel.id] = "p3b1"
                client.timertasks[message.channel.id].cancel()
                client.istimeron[message.channel.id] = False
                await message.channel.send(
                    "Now see if you know the connections. You'll get 5 seconds to type the connection for each group, starting with:")
                r3btimertask = asyncio.create_task(
                    round3btimer(client=client, startercluegroupno=1,
                                                             message=message))  # start the clock
                client.timertasks[
                    message.channel.id] = r3btimertask  # add timer to bot's timer dict for reference in other methods
                client.istimeron[message.channel.id] = True  # state in the bot's boolean dict that the timer is on

async def round3banswercheck(client: commands.Bot, message: discord.Message, currentsubround: int):
    answercorrect = False
    client.timertasks[message.channel.id].cancel()
    client.istimeron[message.channel.id] = False
    for answer in client.questionsinplay[message.channel.id].questioninfo["group " + str(currentsubround)]["answerlist"]:
        if answer in message.content.lower():
            answercorrect = True
            break
    if answercorrect == True:
        await message.channel.send(
            str("Correct! " + client.questionsinplay[message.channel.id].questioninfo["group " + str(currentsubround)][
                "response"]) + "\nThat's 1 point.")
        client.questionsinplay[message.channel.id].wallpoints += 1
    else:
        await message.channel.send(
            str("Not the answer. " + client.questionsinplay[message.channel.id].questioninfo["group " + str(currentsubround)][
                "response"]))
    if currentsubround < 4:
        client.games[message.channel.id] = "p3b" + str(currentsubround + 1)
        r3btimertask = asyncio.create_task(
            round3btimer(client=client, message=message, startercluegroupno=currentsubround+1))  # start the clock
        client.timertasks[
            message.channel.id] = r3btimertask  # add timer to bot's timer dict for reference in other methods
        client.istimeron[message.channel.id] = True  # state in the bot's boolean dict that the timer is on
    elif currentsubround == 4:
        if client.questionsinplay[message.channel.id].wallpoints == 8:
            await message.channel.send("You got 4 points for solving the wall, 4 points for the connections, plus a bonus 2 points!")
            client.questionsinplay[message.channel.id].wallpoints = 10
        await message.channel.send(
            "You got "+ str(client.questionsinplay[message.channel.id].wallpoints)+ " points in total.")
        await message.channel.send("That's the end of the round. Thanks for playing! Type playoc to try another question.")
        client.games[message.channel.id] = "s"

async def round4question(client: commands.Bot, message: discord.Message):
    if message.author == client.user:
        return
    if client.commandedkeys[message.channel.id] == "n":
        client.questionsinplay[message.channel.id].categoryno = 1
        client.questionsinplay[message.channel.id].missingvowelno = 1
        client.commandedkeys[message.channel.id] = "nulla"
        timerlength = 10 * sum(len(category["missingvowels"]) for category in
                           client.questionsinplay[message.channel.id].questioninfo["categories"])
        r4timertask = asyncio.create_task(
            counttimefrommsg(client=client,
                         message=message, channelid=message.channel.id, timelimit=timerlength))  # start the clock
        client.timertasks[
            message.channel.id] = r4timertask  # add timer to bot's timer dict for reference in other methods
        client.istimeron[message.channel.id] = True  # state in the bot's boolean dict that the timer is on

    if client.questionsinplay[message.channel.id].missingvowelno == 1:
        # if the current missing vowel isn't the last in the category
        await message.channel.send("The category is: "+ str(client.questionsinplay[message.channel.id].questioninfo\
          ["categories"][client.questionsinplay[message.channel.id].categoryno-1]["name"]).upper())

    await message.channel.send(client.questionsinplay[message.channel.id].questioninfo
          ["categories"][client.questionsinplay[message.channel.id].categoryno-1]["missingvowels"][client.questionsinplay[message.channel.id].missingvowelno-1])


async def round4answercheck(client: commands.Bot, message: discord.Message):
    answercorrect = False
    for answer in client.questionsinplay[message.channel.id].questioninfo\
          ["categories"][client.questionsinplay[message.channel.id].categoryno-1]\
          ["answers"][client.questionsinplay[message.channel.id].missingvowelno-1]:
        if answer in message.content.lower():
            answercorrect = True
    if answercorrect:
        await message.channel.send("Correct!")
        client.questionsinplay[message.channel.id].round4points +=1
    else:
        await message.channel.send("Not correct, it's: "+client.questionsinplay[message.channel.id].questioninfo
                                   ["categories"][client.questionsinplay[message.channel.id].categoryno - 1][
                                       "answers"][client.questionsinplay[message.channel.id].missingvowelno - 1][0].upper())
        client.questionsinplay[message.channel.id].round4points -= 1

    if client.questionsinplay[message.channel.id].categoryno == len(
        client.questionsinplay[message.channel.id].questioninfo["categories"]) and \
         client.questionsinplay[message.channel.id].missingvowelno == len(
        client.questionsinplay[message.channel.id].questioninfo \
            ["categories"][client.questionsinplay[message.channel.id].categoryno - 1]["missingvowels"]):
        client.timertasks[message.channel.id].cancel()
        client.istimeron[message.channel.id] = False
        client.games[message.channel.id] = "s"
        await message.channel.send("That's the end of the round! Thanks for playing!. You scored "+ str(client.questionsinplay[message.channel.id].round4points)+" points. Type playoc to try another question.")

    else:
        if client.questionsinplay[message.channel.id].missingvowelno != len(
                client.questionsinplay[message.channel.id].questioninfo \
                        ["categories"][client.questionsinplay[message.channel.id].categoryno - 1]["missingvowels"]):
            # if the current missing vowel isn't the last in the category
            print(client.questionsinplay[message.channel.id].missingvowelno)
            client.questionsinplay[message.channel.id].missingvowelno += 1
            print(client.questionsinplay[message.channel.id].missingvowelno)
            print("this one")
        elif client.questionsinplay[message.channel.id].categoryno != len(
                client.questionsinplay[message.channel.id].questioninfo["categories"]) and \
                client.questionsinplay[message.channel.id].missingvowelno == len(
            client.questionsinplay[message.channel.id].questioninfo \
                    ["categories"][client.questionsinplay[message.channel.id].categoryno - 1]["missingvowels"]):
            # if the current missing vowel is the last in the category and there are more categories
            client.questionsinplay[message.channel.id].categoryno += 1
            client.questionsinplay[message.channel.id].missingvowelno = 1
            print(str(client.questionsinplay[message.channel.id].categoryno) + " " + str(
                client.questionsinplay[message.channel.id].missingvowelno))
            print("2nd one")
        await round4question(client=client, message=message)




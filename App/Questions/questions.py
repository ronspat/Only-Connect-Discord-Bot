import random
import requests
import logging

#logging.basicConfig(filename="basic.log", filemode="w",
#                    level=logging.DEBUG, encoding="utf-8",
#                    format='%(levelname)-10s:%(name)-10s:%(message)s')

class Question:

    def __init__(self, questioninfo: dict):
        self.questioninfo = questioninfo

        #round1or2variables
        self.stage = "not started"
        self.cluesgiven = 0

        #round 3 variables
        self.wallpoints = 0
        self.groupsfound = {"group 1": False, "group 2": False, "group 3": False, "group 4": False}
        self.round3lives = 3

        #round4variables
        self.categoryno = -1
        self.missingvowelno = -1
        self.round4points = 0



def getquestionlist(url: str):
    jsonresponseasdict = requests.get(url).json()
    #print(jsonresponseasdict.get("questions"))
    return jsonresponseasdict.get("questions")  # returns questions as list. each question is a dict


def getquestion(questionlist: list, number=None):
    if number is None:
        number = random.randint(0, len(questionlist) - 1)
        return questionlist[number]
    elif 1 <= number <= (len(questionlist)):
        return questionlist[number - 1]
    else:
        print("No question found")
        return


questionlist = getquestionlist("https://onlyconnect.s3.eu-west-2.amazonaws.com/Questions/r3.txt")
q = getquestion(questionlist)
print(q["group 1"]["items"])
print(type(q["group 1"]["items"]))


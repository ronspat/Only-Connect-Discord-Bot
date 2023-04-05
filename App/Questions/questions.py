#A class for questions and methods required to get question info

import random
import requests

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




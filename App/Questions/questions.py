import random
import requests
import logging

#logging.basicConfig(filename="basic.log", filemode="w",
#                    level=logging.DEBUG, encoding="utf-8",
#                    format='%(levelname)-10s:%(name)-10s:%(message)s')

class Question:

    def __init__(self, questioninfo: dict):
        self.questioninfo = questioninfo
        self.stage = "not started"
        self.cluesgiven = 0



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


#questionlist = getquestionlist("https://onlyconnect.s3.eu-west-2.amazonaws.com/Questions/r1.txt")


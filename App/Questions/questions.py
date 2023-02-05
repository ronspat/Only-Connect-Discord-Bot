import random

import requests

class Question:

    def __init__(self, questioninfo: dict):
        self.questioninfo = questioninfo
        self.stage = "not started"
        self.cluesgiven = 0


#     def __init__(self):
#         self.type = None
#         self.id = None
#
#     def questiontime(self):
#         if self.type == 1 or self.type == 2:
#             return 40
#         elif self.type == 3:
#             return 150
#         else:
#             return None

def getquestionlist(url: str):
    jsonresponseasdict = requests.get(url).json()
    #print(jsonresponseasdict.get("questions"))
    return jsonresponseasdict.get("questions")  # returns questions as list. each question is a dict


def getquestion(questionlist: list, number=None):
    if number is None:
        number = random.randint(0, len(questionlist) - 1)
    elif 0 <= number < (len(questionlist) - 1):
        return questionlist[int]
    else:
        print("No question found")
        return None


getquestionlist("https://onlyconnect.s3.eu-west-2.amazonaws.com/Questions/r1.txt")

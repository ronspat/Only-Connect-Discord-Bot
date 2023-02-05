import requests

class Question:

    def __init__(self, questioninfo: dict):
        self.questioninfo = questioninfo
        self.stage = "not started"

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
    print(jsonresponseasdict.get("questions"))
    return type(jsonresponseasdict.get("questions")) # returns questions as list. each question is a dict

def getquestion(questionlist: list, number: int):
    if 0 <= number < len(questionlist):
        return questionlist[int]
    else:
        print("No question found")
        return None

getquestionlist("https://onlyconnect.s3.eu-west-2.amazonaws.com/Questions/r1.txt")





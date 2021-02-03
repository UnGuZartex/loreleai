from loreleai.language.commons import c_pred
from loreleai.learning import Knowledge


def createKnowledge(relativepath: str) -> Knowledge:
    knowledge = Knowledge()
    with open(relativepath, "r") as file:
        for line in file:
            if not line.isspace():
                line = line.replace("\n","")
                if not ":-" in line:
                    lineheader = line.split("(")[0]
                    #headerpredicate = c_pred(lineheader, )
                    print(lineheader)
                else:
                    print("func")
    return knowledge

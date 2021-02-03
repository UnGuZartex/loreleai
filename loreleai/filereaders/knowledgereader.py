import re

from loreleai.language.commons import c_pred
from loreleai.learning import Knowledge


def createKnowledge(relativepath: str) -> Knowledge:
    knowledge = Knowledge()
    s = c_pred("s", 2)
    with open(relativepath, "r") as file:
        for line in file:
            if not line.isspace():
                line = line.replace("\n","")
                if not ":-" in line:
                    lineheader = line.split("(")[0]
                    predicates = re.findall('s?\([^(]*\)', line)
                    allitems = []
                    for item in predicates:
                        if item.startswith("s"):
                            item = item.split(",")
                            item = s(item[0], item[1])
                            allitems.append(item)
                    print(allitems)
                    headerpredicate = c_pred(lineheader, len(predicates))
                    knowledge.add(headerpredicate(allitems))
                    print(lineheader)
                else:
                    print("func")
    print(knowledge.get_all())
    return knowledge

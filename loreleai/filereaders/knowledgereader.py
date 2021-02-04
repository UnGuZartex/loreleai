import re

from loreleai.language.commons import c_pred, c_const, Structure, Atom
from loreleai.learning import Knowledge


def createKnowledge(relativepath: str) -> Knowledge:
    knowledge = Knowledge()
    with open(relativepath, "r") as file:
        for line in file:
            if not line.isspace():
                line = line.replace("\n", "")
                if not ":-" in line:
                    lineheader = line.split("(")[0]
                    predicates = re.findall('s?\([^(]*\)', line)
                    allitems = []
                    for item in predicates:
                        if item.startswith("s"):
                            print("s man")
                            # item = item.replace("s(", "").replace(")","").split(",")
                            # print(item)
                            # allConst = []
                            # for const in item:
                            #     allConst.append(c_const(const))
                            # item = Structure(allConst)
                            # allitems.append(item)
                        else:
                            if "'" in item:
                                item = item.replace("'", "").replace("(", "").replace(")", "").split(",")
                                for const in item:
                                    allitems.append(c_const(const))
                    print(lineheader)
                    print(allitems)
                    headerpredicate = c_pred(lineheader, len(allitems))
                    print(Atom(headerpredicate, allitems))
                    knowledge.add(
                        Atom(headerpredicate, allitems)
                    )

                else:
                    print("func")
    print(knowledge.get_all())
    return knowledge

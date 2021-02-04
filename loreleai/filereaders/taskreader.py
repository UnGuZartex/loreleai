import re

from loreleai.language.commons import c_pred, c_const, List


def readPositiveOfType(inputfile: str, type: str) -> dict:
    totaldict = {}
    with open(inputfile, "r") as file:
        for line in file:
            if not line.isspace():
                line = line.replace("\n", "")
                if line.startswith(type):
                    line = line.replace(type+"_task(", "")
                    line = line[:-2]
                    header = line.split(",")[0]
                    found = re.findall('\[[^\[]*]', line)
                    allitems = []
                    for item in found:
                        item = item.replace("[", "").replace("]","").replace("'","").replace(", ",",")
                        item = item.split(",")
                        item = "".join(item)
                        allLetters = []
                        for letter in item:
                            constLet = c_const(letter)
                            allLetters.append(constLet)
                        item = List(allLetters)
                        allitems.append(item)
                    predicate = c_pred(header, len(allitems))
                    if not header in totaldict:
                        totaldict[header] = set()
                    totaldict[header].add(predicate(*allitems))
    print(totaldict)
    return totaldict

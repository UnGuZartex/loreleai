import re

from loreleai.language.commons import c_pred, c_const


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
                        item = item.replace("[", "").replace("]","").replace("'","").replace(", ",",")  #Maybe different, depending on how we want to represent a string (as list or as string)
                        item = item.split(",")
                        item = "".join(item)
                        item = c_const(item)
                        allitems.append(item)
                    predicate = c_pred(header, len(allitems))
                    print(allitems)
                    if not header in totaldict:
                        totaldict[header] = []
                    totaldict[header].append(predicate(allitems[0], allitems[1]))
    print(totaldict)
    return totaldict

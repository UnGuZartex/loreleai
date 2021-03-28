import re

from pylo.language.commons import c_pred, c_const, List, Structure, c_functor

# Read in all examples from the input file
def readPositiveOfType(inputfile: str, type: str) -> dict:
    totaldict = {}
    # Define a default s functor to represent an example
    s = c_functor("s", 2)
    with open(inputfile, "r") as file:
        for line in file:
            if not line.isspace():
                line = line.replace("\n", "")
                if line.startswith(type):
                    line = line.replace(type+"(", "")
                    line = line[:-2]
                    header = line.split(",")[0]
                    # Find all lists within an example
                    found = re.findall('\[[^\[]*]', line)
                    allitems = []
                    for item in found:
                        item = item.replace("[", "").replace("]","").replace("'","").replace(", ",",")
                        item = item.split(",")
                        item = "".join(item)
                        allLetters = []
                        for letter in item:
                            constLet = c_const("'" + letter + "'")
                            allLetters.append(constLet)
                        item = List(allLetters)
                        allitems.append(item)
                    # Construct the example
                    struct = Structure(s, allitems)
                    if not header in totaldict:
                        totaldict[header] = set()
                    # Add the example to the dictionary
                    totaldict[header].add(c_pred(type, 1)(struct))
    return totaldict

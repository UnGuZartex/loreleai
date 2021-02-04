import re

from loreleai.language.commons import c_pred, c_const, c_var, List
from loreleai.language.lp import Atom, Clause, Not
from loreleai.learning import Knowledge


def createKnowledge(relativepath: str, functionName: str) -> Knowledge:
    knowledge = None
    with open(relativepath, "r") as file:
        for line in file:
            if not line.isspace():
                line = line.replace("\n", "")
                if not ":-" in line:
                    atom = string_to_atom(line, functionName)
                    if knowledge is None:  # For some reason this weird if/else is necessary because lib broke
                        knowledge = Knowledge(atom)
                    else:
                        knowledge._add(
                            atom
                        )

                else:
                    line = line.split(":-")
                    head = line[0] # Atom
                    head = string_to_atom(head, functionName)
                    body = line[1] # List of Atoms
                    allclauses = body.split(";")
                    totalbody = []
                    for clause in allclauses:
                        clause = clause.replace(" ", "")
                        if "\\+" in clause:
                            clause = clause.replace("\\+", "")
                            totalbody.append(Not(string_to_atom(clause, functionName)))
                        else:
                            totalbody.append(string_to_atom(clause, functionName))
                    if knowledge is None:  # For some reason this weird if/else is necessary because lib broke
                        knowledge = Knowledge(Clause(head, totalbody))
                    else:
                        knowledge._add(
                            Clause(head, totalbody)
                        )
    print(knowledge.get_all())
    return knowledge


def string_to_atom(line: str, s: str) -> Atom:
    lineheader = line.split("(")[0]
    predicates = re.findall('(s?\([^()]*\)|[,(][^()]*[,)])', line) # Correct this regex to also find H in write1
    allitems = []
    for item in predicates:
        if item.startswith("s"):
            # Need to handle items with s in it (this is a specific function)
            item = item.replace("s(", s + "(")
            item = string_to_atom(item, s)
            allitems.append(item)
        else:
            string_to_lit(item, allitems)

    headerpredicate = c_pred(lineheader, len(allitems))
    return Atom(headerpredicate, allitems)


def string_to_lit(totalitems, allitems):
    items = totalitems.replace("(", "").replace(")", "").split(",")
    if len(items) > 1:
        for item in items:
            string_to_lit_help(item, allitems)
    else:
        string_to_lit_help(items[0], allitems)


def string_to_lit_help(item, allitems):
    if "[" in item:
        item = item.replace("[", "").replace("]", "").split("|")
        totalList = []
        for lit in item:
            string_to_lit(lit, totalList)
        allitems.append(List(totalList))
    elif "'" in item:
        item = item.replace("'", "").replace(",","")
        if item != "":
            allitems.append(c_const(item))

    else:
        item = item.replace(",", "")
        if item != "":
            allitems.append(c_var(item))
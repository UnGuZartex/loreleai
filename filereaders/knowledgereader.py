# TODO Probably useless file now... although we still need the predicates :)

import re

from pylo.language.commons import c_pred, c_const, c_var, List, Predicate
from pylo.language.lp import Atom, Clause, Not
from typing import Tuple, Set

from loreleai.learning import Knowledge

IGNORECOUNTER = 0


def createKnowledge(relativepath: str, functionName: str) -> Tuple[Knowledge, Set[Predicate]]:
    knowledge = None
    predicateList = list()
    with open(relativepath, "r") as file:
        for line in file:
            if not line.isspace():
                line = line.replace("\n", "")
                if not ":-" in line:
                    atom = string_to_atom(line, functionName, predicateList)
                    if knowledge is None:  # For some reason this weird if/else is necessary because lib broke
                        knowledge = Knowledge(atom)
                    else:
                        knowledge._add(
                            atom
                        )

                else:
                    line = line.split(":-")
                    head = line[0] # Atom
                    head = string_to_atom(head, functionName, predicateList)
                    body = line[1] # List of Atoms
                    allclauses = body.split(";")
                    totalbody = []
                    for clause in allclauses:
                        clause = clause.replace(" ", "")
                        if "\\+" in clause:
                            clause = clause.replace("\\+", "")
                            totalbody.append(Not(string_to_atom(clause, functionName, predicateList)))
                        else:
                            totalbody.append(string_to_atom(clause, functionName, predicateList))
                    if knowledge is None:  # For some reason this weird if/else is necessary because lib broke
                        knowledge = Knowledge(Clause(head, totalbody))
                    else:
                        knowledge._add(
                            Clause(head, totalbody)
                        )
    return knowledge, predicateList


def string_to_atom(line: str, s: str, predicateList: list) -> Atom:
    lineheader = line.split("(")[0]
    predicates = re.findall('(s?\([^()]*\)|[,(][^()]*[,)])', line) # Correct this regex to also find H in write1
    allitems = []
    for item in predicates:
        if item.startswith("s"):
            # Need to handle items with s in it (this is a specific function)
            item = item.replace("s(", s + "(")
            item = string_to_atom(item, s, predicateList)
            allitems.append(item)
        else:
            string_to_lit(item, allitems)

    headerpredicate = c_pred(lineheader, len(allitems))
    predicateList.append(headerpredicate)
    return Atom(headerpredicate, allitems)


def string_to_lit(totalitems, allitems):
    items = totalitems.replace("(", "").replace(")", "").split(",")
    if len(items) > 1:
        for item in items:
            string_to_lit_help(item, allitems)
    else:
        string_to_lit_help(items[0], allitems)


def string_to_lit_help(item, allitems):
    global IGNORECOUNTER
    if "[" in item:
        item = item.replace("[", "").replace("]", "").split("|")
        totalList = []
        for lit in item:
            string_to_lit(lit, totalList)
        allitems.append(List(totalList))
    elif "'" in item:
        item = item.replace(",","")
        if item != "":
            allitems.append(c_const(item))

    else:
        item = item.replace(",", "")
        if item != "":
            if "_" in item:
                item += str(IGNORECOUNTER)
                item = "F" + item
                IGNORECOUNTER += 1
            allitems.append(c_var(item))
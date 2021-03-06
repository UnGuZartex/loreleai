import random
import typing
from math import factorial

import numpy
from pylo.engines import SWIProlog
from pylo.language.commons import c_pred, Clause, Procedure, Atom, Structure, List
from orderedset import OrderedSet

from filereaders.knowledgereader import createKnowledge
from filereaders.taskreader import readPositiveOfType
from loreleai.learning import plain_extension, TopDownHypothesisSpace, has_singleton_vars, has_duplicated_literal

MAX_STRING_LENGTH = 120
prolog = SWIProlog()


def put_into_pool(candidate_pool: OrderedSet, candidates: typing.Union[Clause, Procedure, typing.Sequence]) -> None:
    if isinstance(candidates, Clause):
        candidate_pool.add(candidates)
    else:
        candidate_pool |= candidates


def clause_to_list(current_cand: Clause, filtered_predicates):
    body = current_cand.get_body()
    listencoding = [0] * len(filtered_predicates)
    for predicate in body.get_predicates():
        print(filtered_predicates)
        listencoding[filtered_predicates.index(predicate)] += 1
    return listencoding


def var_coeff(current_cand: Clause, filtered_predicates):
    body = current_cand.get_body()
    allliterals = body.get_literals()
    totalliterals = len(allliterals)
    connections = [0]*len(filtered_predicates)
    for literal in allliterals:
        all_variables1 = literal.get_variables()
        index = filtered_predicates.index(literal.get_predicate())
        for literal2 in allliterals:
            if literal != literal2:
                all_variables2 = literal2.get_variables()
                for variable in all_variables1:
                    if variable in all_variables2:
                        connections[index] += 1
                        break
    for index in range(len(connections)):
        if totalliterals > 1:
            connections[index] /= (totalliterals-1)
        else:
            connections[index] = 0
    return ",".join([str(elem) for elem in connections])


def encode_clause(current_cand: Clause, filtered_predicates):
    listencoding = clause_to_list(current_cand, filtered_predicates)
    encoded_clause = ",".join([str(elem) for elem in listencoding])
    encoded_clause += "," + str(len(current_cand))
    encoded_clause += "," + str(var_coeff(current_cand, filtered_predicates))
    return encoded_clause


def encode_string(string: List):
    result = [0] * MAX_STRING_LENGTH
    arguments = string.arguments
    for index in range(len(arguments)):
        result[index] = ord(arguments[index].name.replace("'", ""))
    return result


def encode_example(example: Structure):
    input = example.arguments[0]
    output = example.arguments[1]
    encoded_input = encode_string(input)
    input_string = ",".join([str(elem) for elem in encoded_input])
    encoded_output = encode_string(output)
    output_string = ",".join([str(elem) for elem in encoded_output])
    return input_string + "," + output_string


def get_input_data(current_cand: Clause, example: Atom, filtered_predicates):
    encoded_clause = encode_clause(current_cand, filtered_predicates)
    encoded_example = encode_example(
        example.arguments[0])  # Don't mind this warning (it works but python typing is weird :p)
    return encoded_clause + "," + encoded_example


def get_nn_input_data(current_cand: Clause, example: Atom, filtered_predicates):
    x_clause = []
    x_input = []
    x_output = []
    inputstring = get_input_data(current_cand, example, filtered_predicates)
    line = inputstring.replace("\n", "")
    list_of_floats = [float(item) for item in line.split(",")]
    x_clause.append(list_of_floats[:45])
    x_input.append(list_of_floats[45:165])
    x_output.append(list_of_floats[165:])
    x_clause = numpy.array(x_clause)
    x_input = numpy.array(x_input)
    x_output = numpy.array(x_output)
    x = [x_clause, x_input, x_output]
    return x


def find_difference(encoded_current_cand, encoded_expansion):
    for index in range(len(encoded_current_cand)):
        if encoded_expansion[index] != encoded_current_cand[index]:
            return index
    return None


def get_output_data(current_cand, expansions, example,
                    filtered_predicates):  # We might have to look into a way to make this faster because slowbro :'(

    encoded_current_cand = clause_to_list(current_cand, filtered_predicates)
    total_occurrences = [0] * len(filtered_predicates)
    total_covered = [0] * len(filtered_predicates)
    for expansion in expansions:
        encoded_expansion = clause_to_list(expansion, filtered_predicates)
        clause_index = find_difference(encoded_current_cand, encoded_expansion)
        if clause_index:
            total_occurrences[clause_index] += 1
            prolog.asserta(expansion)
            if prolog.has_solution(example):
                total_covered[clause_index] += 1
            prolog.retract(expansion)

    covered = [0] * len(filtered_predicates)

    for index in range(len(total_occurrences)):
        if total_occurrences[index] != 0:
            if total_covered[index] != 0:
                total_covered[index] /= total_occurrences[index]
                covered[index] = 1
            else:
                total_covered[index] = 0
                covered[index] = 0
        else:
            total_covered[index] = 0
            covered[index] = 0
    return ",".join([str(elem) for elem in total_covered]), ",".join([str(elem) for elem in covered])


def process_expansions(exps: typing.Sequence[Clause],
                       hypothesis_space: TopDownHypothesisSpace) -> typing.Sequence[Clause]:
    # check if every clause has solutions
    exps = [(cl, prolog.has_solution(*cl.get_body().get_literals())) for cl in exps]
    new_exps = []

    for ind in range(len(exps)):
        if exps[ind][1]:
            # keep it if it has solutions
            new_exps.append(exps[ind][0])
        else:
            # remove from hypothesis space if it does not
            hypothesis_space.remove(exps[ind][0])

    return new_exps

def main():
    f1 = open("processeddata_average.csv", "a")
    f2 = open("processeddata_covered.csv", "a")
    prolog.consult("../inputfiles/StringTransformations_BackgroundKnowledge.pl")

    amount_of_clauses = 500
    chosen_pred = "t"
    minlength = 0
    max_factor_per_length = 4

    _, predicates = createKnowledge("../inputfiles/StringTransformations_BackgroundKnowledge.pl",
                                                 chosen_pred)
    train = readPositiveOfType("../inputfiles/StringTransformationProblems", "train_task")

    totalextension = []
    filtered_predicates = []

    for predicate in predicates:
        if predicate.name not in ["s", chosen_pred] and predicate not in filtered_predicates:
            totalextension.append(lambda x, predicate=predicate: plain_extension(x, predicate, connected_clauses=True))
            filtered_predicates.append(predicate)

    # create the hypothesis space
    hs = TopDownHypothesisSpace(primitives=totalextension,
                                head_constructor=c_pred("train_task", 1),
                                expansion_hooks_reject=[lambda x, y: has_singleton_vars(x, y),
                                                        lambda x, y: has_duplicated_literal(x, y)])
    clauses_used = 0
    possible_candidates = OrderedSet()
    put_into_pool(possible_candidates, hs.get_current_candidate())
    amount_of_length = 0
    previouslength = 0

    while clauses_used < amount_of_clauses:
        current_cand = possible_candidates.pop(0)
        # expand the candidate
        _ = hs.expand(current_cand)
        # this is important: .expand() method returns candidates only the first time it is called;
        #     if the same node is expanded the second time, it returns the empty list
        #     it is safer than to use the .get_successors_of method
        exps = hs.get_successors_of(current_cand)
        expa = process_expansions(exps,hs)
        put_into_pool(possible_candidates, expa)

        if previouslength < len(current_cand):
            amount_of_length = 0

        if random.random() < 0.5 and len(current_cand) > minlength and amount_of_length < max_factor_per_length*len(current_cand):
            for problem in train:
                for example in train.get(problem):
                    if random.random() < 0.25:
                        input = get_input_data(current_cand, example, filtered_predicates)
                        output, output2 = get_output_data(current_cand, expa, example, filtered_predicates)
                        f1.write(input + "," + output + "\n")
                        f2.write(input + "," + output2 + "\n")
            clauses_used += 1
            amount_of_length += 1
        previouslength = len(current_cand)

if __name__ == "__main__":
    main()

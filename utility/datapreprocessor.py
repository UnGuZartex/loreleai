import random
import typing
from math import factorial

from pylo.engines import SWIProlog
from pylo.language.commons import c_pred, Clause, Procedure, Atom, Structure, List
from orderedset import OrderedSet

from filereaders.knowledgereader import createKnowledge
from filereaders.taskreader import readPositiveOfType
from loreleai.learning import plain_extension, TopDownHypothesisSpace, has_singleton_vars, has_duplicated_literal

MAX_STRING_LENGTH = 120


def put_into_pool(candidate_pool: OrderedSet, candidates: typing.Union[Clause, Procedure, typing.Sequence]) -> None:
    if isinstance(candidates, Clause):
        candidate_pool.add(candidates)
    else:
        candidate_pool |= candidates


def clause_to_list(current_cand: Clause, filtered_predicates):
    body = current_cand.get_body()
    listencoding = [0] * len(filtered_predicates)
    for predicate in body.get_predicates():
        listencoding[filtered_predicates.index(predicate)] += 1
    return listencoding


def var_coeff(current_cand: Clause):
    body = current_cand.get_body()
    allliterals = body.get_literals()
    totalliterals = len(allliterals)
    connections = {}
    for literal in allliterals:
        all_variables = literal.get_variables()
        for i in range(len(all_variables)):
            for j in range(i, len(all_variables)):
                if all_variables[i] != all_variables[j]:
                    if not connections.get(all_variables[i]):
                        connections[all_variables[i]] = list()
                    connections.get(all_variables[i]).append(all_variables[j])
    diff_vars = len(connections)
    full_combined = factorial(diff_vars) * totalliterals
    total_connections = 0
    for var in connections:
        total_connections += len(connections.get(var))
    return str(total_connections / full_combined)


def encode_clause(current_cand: Clause, filtered_predicates):
    listencoding = clause_to_list(current_cand, filtered_predicates)
    encoded_clause = ",".join([str(elem) for elem in listencoding])
    encoded_clause += "," + str(len(current_cand))
    encoded_clause += "," + str(var_coeff(current_cand))
    return encoded_clause


def encode_string(string: List):  # TODO hier dus goeie encoding voor maken idk hoe though
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


def find_difference(encoded_current_cand, encoded_expansion):
    for index in range(len(encoded_current_cand)):
        if encoded_expansion[index] != encoded_current_cand[index]:
            return index
    return None


def get_output_data(current_cand, expansions, example,
                    filtered_predicates):  # We might have to look into a way to make this faster because slowbro :'(
    prolog = SWIProlog()

    encoded_current_cand = clause_to_list(current_cand, filtered_predicates)
    total_occurrences = [0] * len(filtered_predicates)
    total_covered = [0] * len(filtered_predicates)
    for expansion in expansions:
        encoded_expansion = clause_to_list(expansion, filtered_predicates)
        clause_index = find_difference(encoded_current_cand, encoded_expansion)
        if clause_index:
            total_occurrences[clause_index] += 1
            prolog.consult("../inputfiles/StringTransformations_BackgroundKnowledge.pl")
            prolog.asserta(expansion)
            if prolog.has_solution(example):
                total_covered[clause_index] += 1
            prolog.retract(expansion)

    for index in range(len(total_occurrences)):
        if total_occurrences[index] != 0:
            total_covered[index] /= total_occurrences[index]
        else:
            total_covered[index] = 0
    return ",".join([str(elem) for elem in total_covered])


def remove_random(exps):
    expa = []
    for exp in exps:
        if random.random() < 0.1:
            expa.append(exp)
    return expa


def main():
    f = open("processeddata.csv", "a")
    amount_of_clauses = 2
    chosen_pred = "t"
    minlength = 2

    backgroundknow, predicates = createKnowledge("../inputfiles/StringTransformations_BackgroundKnowledge.pl",
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

    while clauses_used < amount_of_clauses:

        current_cand = possible_candidates.pop(0)
        # expand the candidate
        _ = hs.expand(current_cand)
        # this is important: .expand() method returns candidates only the first time it is called;
        #     if the same node is expanded the second time, it returns the empty list
        #     it is safer than to use the .get_successors_of method
        exps = hs.get_successors_of(current_cand)
        exps = remove_random(exps)
        put_into_pool(possible_candidates, exps)

        if random.random() < 0.1 and len(current_cand) > minlength:
            for problem in train:
                for example in train.get(problem):
                    if random.random() < 0.1:
                        input = get_input_data(current_cand, example, filtered_predicates)
                        output = get_output_data(current_cand, exps, example, filtered_predicates)
                        f.write(input + "," + output + "\n")
            clauses_used += 1


main()

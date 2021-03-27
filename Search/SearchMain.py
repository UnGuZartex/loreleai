import random
import string

from pylo.language.commons import c_functor, List, Structure

from Search.NeuralSearcher1 import NeuralSearcher1
from filereaders.knowledgereader import createKnowledge
from filereaders.taskreader import readPositiveOfType
from loreleai.language.lp import c_pred, Clause, Procedure, Atom
from loreleai.learning.hypothesis_space import TopDownHypothesisSpace
from loreleai.learning.language_filtering import has_singleton_vars, has_duplicated_literal, connected_clause, \
    has_g1_same_vars_in_literal, has_double_recursion, has_duplicated_var_set, head_first, only_1_pred_for_1_var, \
    has_new_input, has_not_previous_output_as_input, has_unexplained_last_var, has_endless_recursion, \
    has_unexplained_last_var_strict
from loreleai.learning.language_manipulation import plain_extension
from loreleai.learning.task import Task, Knowledge
from loreleai.reasoning.lp.prolog import SWIProlog, Prolog


def train_task(task_id: string, pos_multiplier: int, neg_example_offset: int):
    backgroundknow, predicates = createKnowledge("../inputfiles/StringTransformations_BackgroundKnowledge.pl", task_id)
    #train = readPositiveOfType("../inputfiles/StringTransformationProblems", "train_task")
    test = readPositiveOfType("../inputfiles/StringTransformationProblems", "test_task")

    neg = set()
    pos = test.get(task_id)
    test.pop(task_id)
    neg_amount = len(pos) * pos_multiplier + neg_example_offset
    for i in range(neg_amount):
        # Choose random task to sample neg example
        chosen_task_id = random.choice(list(test.keys()))

        # Choose random example and remove so it doesn't get picked again
        chosen_neg_example = random.sample(test[chosen_task_id], 1)[0]
        test[chosen_task_id].remove(chosen_neg_example)

        # Add example to negative example list
        neg.add(chosen_neg_example)

    task = Task(positive_examples=pos, negative_examples=neg)

    # Calculate predicates
    total_predicates = []
    filtered_predicates = []
    for predicate in predicates:
        if predicate.name not in ["s", task_id] and predicate not in filtered_predicates:
            total_predicates.append(
                lambda x, predicate=predicate: plain_extension(x, predicate, connected_clauses=True))
            filtered_predicates.append(predicate)


    # TODO recursion
    # create the hypothesis space
    hs = TopDownHypothesisSpace(primitives=total_predicates,
                                head_constructor=c_pred("test_task", 1),
                                recursive_procedures=True,
                                expansion_hooks_keep=[lambda x, y: connected_clause(x, y),
                                                      lambda x, y: only_1_pred_for_1_var(x, y),
                                                      lambda x, y: head_first(x, y)],
                                expansion_hooks_reject=[#lambda x, y: has_singleton_vars(x, y),
                                                        # Singleton-vars constraint is reduced to this constraint
                                                        lambda x, y: has_not_previous_output_as_input(x, y), # Strict
                                                        #lambda x, y: has_new_input(x, y), # Not as strict
                                                        #lambda x, y: has_unexplained_last_var(x, y), # For the 'write' predicate
                                                        lambda x, y: has_unexplained_last_var_strict(x, y), # Strict version of above
                                                        lambda x, y: has_duplicated_literal(x, y),
                                                        lambda x, y: has_g1_same_vars_in_literal(x, y),
                                                        lambda x, y: has_duplicated_var_set(x, y),
                                                        lambda x, y: has_double_recursion(x, y),
                                                        lambda x, y: has_endless_recursion(x, y)])

    # create Prolog and learner instance
    prolog = SWIProlog()
    learner = NeuralSearcher1(solver_instance=prolog, primitives=filtered_predicates,
                              model_location="../utility/Saved_model_covered", max_body_literals=15,
                              amount_chosen_from_nn=10, filter_amount=500, threshold=0.1)

    program = learner.learn(task, "../inputfiles/StringTransformations_BackgroundKnowledge.pl", hs)
    print(program)


    ''''
    
    # NN keuze
    [is_lowercase_aux is_space not_space not_lowercase is_uppercase_aux write1
     copyskip1 not_uppercase is_lowercase mk_lowercase]
     
    # alle expansies voor filteren
    [test_task(A): - is_empty(A), test_task(A): - not_empty(A), test_task(A): - is_space(A), test_task(A): - not_space(
        A), test_task(A): - is_uppercase(A), test_task(A): - is_uppercase_aux(A), test_task(A): - not_uppercase(
        A), test_task(A): - is_lowercase(A), test_task(A): - is_lowercase_aux(A), test_task(A): - not_lowercase(
        A), test_task(A): - is_letter(A), test_task(A): - not_letter(A), test_task(A): - is_number(A), test_task(
        A): - is_number_aux(A), test_task(A): - not_number(A), test_task(A): - skip1(A, B), test_task(A): - copy1(A,
                                                                                                                  B), test_task(
        A): - write1(A, B, C), test_task(A): - copyskip1(A, B), test_task(A): - mk_uppercase(A, B), test_task(
        A): - convert_case(A, B), test_task(A): - mk_lowercase(A, B)]
        
    # triplets
    [ < Search.Triplet.Triplet
    object
    at
    0x7f4d3d35bca0 >, < Search.Triplet.Triplet
    object
    at
    0x7f4d3f68e040 >, < Search.Triplet.Triplet
    object
    at
    0x7f4d3d3c9ee0 >, < Search.Triplet.Triplet
    object
    at
    0x7f4d3d3c9520 >, < Search.Triplet.Triplet
    object
    at
    0x7f4d3d3c9b50 >, < Search.Triplet.Triplet
    object
    at
    0x7f4d3d3c91f0 >, < Search.Triplet.Triplet
    object
    at
    0x7f4d3d3c97c0 >]
    
    # triplets vertaald
    [(-0.29411764705882354, -5, 1, 'test_task(A) :- write1(A,B,C)', test_task(A) :- write1(A, B, C)), (
    -0.0, 0, 1, 'test_task(A) :- copyskip1(A,B)', test_task(A) :- copyskip1(A, B)), (
    200, 0, 1, 'test_task(A) :- is_space(A)', test_task(A) :- is_space(A)), (
    200, 0, 1, 'test_task(A) :- is_uppercase_aux(A)', test_task(A) :- is_uppercase_aux(A)), (
    200, 0, 1, 'test_task(A) :- is_lowercase(A)', test_task(A) :- is_lowercase(A)), (
    200, 0, 1, 'test_task(A) :- is_lowercase_aux(A)', test_task(A) :- is_lowercase_aux(A)), (
    200, 0, 1, 'test_task(A) :- mk_lowercase(A,B)', test_task(A) :- mk_lowercase(A, B))]
    12'''


def main():
    train_task("b3", 2, 2)


if __name__ == "__main__":
    main()

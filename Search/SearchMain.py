import random
import string
import sys

from Search.NeuralSearcher1 import NeuralSearcher1
from filereaders.knowledgereader import createKnowledge
from filereaders.taskreader import readPositiveOfType
from loreleai.language.lp import c_pred
from loreleai.learning.hypothesis_space import TopDownHypothesisSpace
from loreleai.learning.language_filtering import has_duplicated_literal, connected_clause, \
    has_g1_same_vars_in_literal, has_double_recursion, has_duplicated_var_set, head_first, only_1_pred_for_1_var, \
    has_not_previous_output_as_input, has_endless_recursion, \
    has_unexplained_last_var_strict
from loreleai.learning.language_manipulation import plain_extension
from loreleai.learning.task import Task
from loreleai.reasoning.lp.prolog import SWIProlog

# create Prolog and learner instance
prolog = SWIProlog()


def train_task(task_id: string, pos_multiplier: int, neg_example_offset: int, nn_amount: int, pos=None, neg=None):
    # Load needed files
    bk, predicates = createKnowledge("../inputfiles/StringTransformations_BackgroundKnowledge.pl", task_id)

    if pos is None and neg is None:
        pos, neg = generate_examples(task_id, pos_multiplier, neg_example_offset)

    task = Task(positive_examples=pos, negative_examples=neg)

    # Calculate predicates
    total_predicates = []
    filtered_predicates = []
    for predicate in predicates:
        if predicate.name not in ["s", task_id] and predicate not in filtered_predicates:
            total_predicates.append(
                lambda x, pred=predicate: plain_extension(x, pred, connected_clauses=True))
            filtered_predicates.append(predicate)

    # create the hypothesis space
    hs = TopDownHypothesisSpace(primitives=total_predicates,
                                head_constructor=c_pred("test_task", 1),
                                recursive_procedures=True,
                                expansion_hooks_keep=[lambda x, y: connected_clause(x, y),
                                                      lambda x, y: only_1_pred_for_1_var(x, y),
                                                      lambda x, y: head_first(x, y)],
                                expansion_hooks_reject=[  # lambda x, y: has_singleton_vars(x, y),
                                    # Singleton-vars constraint is reduced to this constraint
                                    lambda x, y: has_not_previous_output_as_input(x, y),  # Strict
                                    # lambda x, y: has_new_input(x, y), # Not as strict
                                    # lambda x, y: has_unexplained_last_var(x, y), # For the 'write' predicate
                                    lambda x, y: has_unexplained_last_var_strict(x, y),  # Strict version of above
                                    lambda x, y: has_duplicated_literal(x, y),
                                    lambda x, y: has_g1_same_vars_in_literal(x, y),
                                    lambda x, y: has_duplicated_var_set(x, y),
                                    lambda x, y: has_double_recursion(x, y),
                                    lambda x, y: has_endless_recursion(x, y)])

    learner = NeuralSearcher1(solver_instance=prolog, primitives=filtered_predicates,
                              model_location="../utility/Saved_model_covered", max_body_literals=10,
                              amount_chosen_from_nn=nn_amount, filter_amount=30, threshold=0.1)

    # Try to learn the program
    program, ss = learner.learn(task, "../inputfiles/StringTransformations_BackgroundKnowledge.pl", hs)
    print(program)

    return ss


def test():
    test_tasks = ["b249", "b38", "b123"]  # "b308", "b134", "b188"]
    ss = []
    nn_amount = [22, 20, 18, 16, 14, 12]

    for i in range(len(test_tasks)):
        pos, neg = generate_examples(test_tasks[i], 5, 0)

        for j in range(len(nn_amount)):

            output = train_task(test_tasks[i], 5, 0, nn_amount[j], pos, neg)
            output.set_task(test_tasks[i])
            output.set_nn_amount(nn_amount[j])
            print("DONE EXAMPLE")
            ss.append(output)

    ostd = sys.stdout
    with open('tests', 'w') as f:
        sys.stdout = f

        for s in ss:
            print(s)

        sys.stdout = ostd

def generate_examples(task_id, pos_multiplier, neg_example_offset):
    test = readPositiveOfType("../inputfiles/StringTransformationProblems", "test_task")

    # Prepare examples
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

    return pos, neg


def main():
    test()


if __name__ == "__main__":
    main()

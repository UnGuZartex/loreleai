import random
import string

from Search.NeuralSearcher1 import NeuralSearcher1
from filereaders.knowledgereader import createKnowledge
from filereaders.taskreader import readPositiveOfType
from loreleai.language.lp import c_pred, Clause, Procedure, Atom
from loreleai.learning.hypothesis_space import TopDownHypothesisSpace
from loreleai.learning.language_filtering import has_singleton_vars, has_duplicated_literal
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
        chosen_neg_example = random.sample(test[chosen_task_id],1)[0]
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
                                expansion_hooks_keep=[lambda x, y: connected_clause(x, y)]
                                expansion_hooks_reject=[lambda x, y: has_singleton_vars(x, y)]#,
                                                        #lambda x, y: has_duplicated_literal(x, y)])

    # create Prolog and learner instance
    prolog = SWIProlog()
    learner = NeuralSearcher1(solver_instance=prolog, primitives=filtered_predicates,
                              model_location="../utility/Saved_model_covered", max_body_literals=120,
                              amount_chosen_from_nn=6)

    program = learner.learn(task, "../inputfiles/StringTransformations_BackgroundKnowledge.pl", hs)
    print(program)


def main():
    train_task("b45", 2, 2)


if __name__ == "__main__":
    main()

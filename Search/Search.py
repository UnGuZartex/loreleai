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


def train_task(task_id: string):
    backgroundknow, predicates = createKnowledge("../inputfiles/StringTransformations_BackgroundKnowledge.pl", task_id)
    train = readPositiveOfType("../inputfiles/StringTransformationProblems", "train_task")
    test = readPositiveOfType("../inputfiles/StringTransformationProblems", "test_task")

    pos = test.get("b45")
    neg = set()  # TODO negatieve voorbeelden genereren
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
                                head_constructor=c_pred("train_task", 1),
                                expansion_hooks_reject=[lambda x, y: has_singleton_vars(x, y),
                                                        lambda x, y: has_duplicated_literal(x, y)])

    # create Prolog and learner instance
    prolog = SWIProlog()
    learner = NeuralSearcher1(solver_instance=prolog, primitives=total_predicates,
                              model_location="../utility/Saved_model", max_body_literals=3,
                              amount_chosen_from_nn=3)

    program = learner.learn(task, "../inputfiles/StringTransformations_BackgroundKnowledge.pl", hs)
    print(program)


def main():
    train_task("b45")


if __name__ == "__main__":
    main()

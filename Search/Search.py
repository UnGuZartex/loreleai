import string
import typing
from abc import ABC, abstractmethod

from orderedset import OrderedSet

from Search.NeuralSearcher import NeuralSearcher
from filereaders.knowledgereader import createKnowledge
from filereaders.taskreader import readPositiveOfType
from loreleai.language.lp import c_pred, Clause, Procedure, Atom
from loreleai.learning.hypothesis_space import TopDownHypothesisSpace
from loreleai.learning.language_filtering import has_singleton_vars, has_duplicated_literal
from loreleai.learning.language_manipulation import plain_extension
from loreleai.learning.task import Task, Knowledge
from loreleai.reasoning.lp.prolog import SWIProlog, Prolog

task_id = "b45"
backgroundknow, predicates = createKnowledge("../inputfiles/StringTransformations_BackgroundKnowledge.pl", task_id)
train = readPositiveOfType("../inputfiles/StringTransformationProblems", "train_task")
test = readPositiveOfType("../inputfiles/StringTransformationProblems", "test_task")

pos = test.get("b45")
neg = set() # TODO negatieve voorbeelden genereren
task = Task(positive_examples=pos, negative_examples=neg)

# create Prolog instance
prolog = SWIProlog()
learner = NeuralSearcher(solver_instance=prolog, model_location="../utility/Saved_model", max_body_literals=3,
                         amount_chosen_from_nn=3)
# Calculate predicates
total_predicates = []
filtered_predicates = []
for predicate in predicates:
    if predicate.name not in ["s", task_id] and predicate not in filtered_predicates:
        total_predicates.append(lambda x, predicate=predicate: plain_extension(x, predicate, connected_clauses=True))
        filtered_predicates.append(predicate)

# TODO recursion
# create the hypothesis space
hs = TopDownHypothesisSpace(primitives=total_predicates,
                            head_constructor=c_pred("train_task", 1),
                            expansion_hooks_reject=[lambda x, y: has_singleton_vars(x, y),
                                                    lambda x, y: has_duplicated_literal(x, y)])

program = learner.learn(task, "../inputfiles/StringTransformations_BackgroundKnowledge.pl", filtered_predicates, hs)
print(program)
import typing
from abc import abstractmethod, ABC

from orderedset import OrderedSet

from Search.AbstractNeuralSearcher import AbstractNeuralSearcher
from Search.AbstractSearcher import AbstractSearcher
from loreleai.learning.hypothesis_space import TopDownHypothesisSpace
from loreleai.learning.task import Task
from loreleai.reasoning.lp.prolog import Prolog

from loreleai.language.lp import (
    Predicate,
    Clause,
    Procedure,
    Atom,
    Body,
    Recursion,
)
from utility.datapreprocessor import get_nn_input_data


class NeuralSearcher1(AbstractNeuralSearcher):
    def __init__(self, solver_instance: Prolog, primitives, model_location, max_body_literals=4,
                 amount_chosen_from_nn=3):
        super().__init__(solver_instance, primitives, model_location, max_body_literals=4, amount_chosen_from_nn=3)

    def filter_examples(self, examples: Task) -> Task:
        # TODO
        raise NotImplementedError()

    def process_output(self, nn_output):
        # TODO
        raise NotImplementedError()

    def update_score(self, current_score_vector, new_score_vector):
        # TODO
        raise NotImplementedError()

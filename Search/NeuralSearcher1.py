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
        super().__init__(solver_instance, primitives, model_location, max_body_literals, amount_chosen_from_nn)

    def filter_examples(self, examples: Task) -> Task:
        pos, _ = examples.get_examples()
        return pos

    def process_output(self, nn_output):
        return nn_output

    def update_score(self, current_score_vector, new_score_vector):
        # TODO per score nog, miss nog current_cand als ftieparam om hier * weight te doen
        return current_score_vector + new_score_vector

    def get_initial_weights(self, examples: Task) -> dict:
        example_weights = {}
        for example in examples:
            example_weights[example] = 1

        return example_weights

    def set_example_weights(self, previous_cand: typing.Union[Clause, Procedure],
                            current_cand: typing.Union[Clause, Procedure], examples: Task):
        # TODO update weights
        self.example_weights[current_cand] = self.get_initial_weights(self, examples)


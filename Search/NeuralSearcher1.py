import typing
from abc import abstractmethod, ABC

import numpy
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
                 amount_chosen_from_nn=3, filter_amount=2, threshold=0.5):
        super().__init__(solver_instance, primitives, model_location, max_body_literals, amount_chosen_from_nn, filter_amount)
        self.threshold = threshold

    def filter_examples(self, examples: Task) -> Task:
        pos, _ = examples.get_examples()
        return pos

    def process_output(self, nn_output):
        output_array = numpy.zeros(len(nn_output))
        for index in range(len(nn_output)):
            value = nn_output[index]
            if value > self.threshold:
                output_array[index] = 1
            else:
                output_array[index] = 0
        return output_array

    def update_score(self, current_cand: typing.Union[Clause, Recursion, Body], example,
                     current_score_vector, new_score_vector):
        return current_score_vector + self.example_weights[current_cand][example] * new_score_vector

    def get_initial_weights(self, examples: Task) -> dict:
        example_weights = {}
        for examples in examples.get_examples():
            for example in examples:
                example_weights[example] = 1

        return example_weights

    def set_example_weights(self, previous_cand: typing.Union[Clause, Procedure],
                            current_cand: typing.Union[Clause, Procedure], examples: Task):
        # TODO update weights
        self.example_weights[current_cand] = self.get_initial_weights(examples)


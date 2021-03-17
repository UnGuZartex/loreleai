import typing
from abc import abstractmethod
from queue import PriorityQueue

import numpy
from orderedset import OrderedSet

from functools import cmp_to_key

from Search.AbstractSearcher import AbstractSearcher
from Search.Triplet import Triplet
from loreleai.learning.hypothesis_space import TopDownHypothesisSpace
from loreleai.learning.task import Task
from loreleai.reasoning.lp.prolog import Prolog
from tensorflow import keras

from loreleai.language.lp import (
    Predicate,
    Clause,
    Procedure,
    Atom,
    Body,
    Recursion,
)
from utility.datapreprocessor import get_nn_input_data, clause_to_list, find_difference


class AbstractNeuralSearcher(AbstractSearcher):
    def __init__(self, solver_instance: Prolog, primitives, model_location, max_body_literals, amount_chosen_from_nn,
                 filter_amount):
        super().__init__(solver_instance, primitives)
        self._max_body_literals = max_body_literals
        self.amount_chosen_from_nn = amount_chosen_from_nn
        self.filter_amount = filter_amount
        self.model = keras.models.load_model(model_location, compile=True)

    def initialise_pool(self):
        self._candidate_pool = PriorityQueue()

    def put_into_pool(self, candidates) -> None:

        for candidate in candidates:
            self._candidate_pool.put(candidate)

    def get_from_pool(self) -> Clause:
        return self._candidate_pool.get()[-1]

    def evaluate(self, examples: Task, clause: Clause) -> typing.Union[int, float]:
        covered = self._execute_program(examples, clause)

        pos, neg = examples.get_examples()

        covered_pos = pos.intersection(covered)
        covered_neg = neg.intersection(covered)

        print(len(covered_neg))
        print(len(covered_pos))
        if len(covered_neg) > 0:
            return 0
        else:
            return len(covered_pos)

    def stop_inner_search(self, eval: typing.Union[int, float], examples: Task, clause: Clause) -> bool:
        if eval > 0:
            return True
        else:
            return False

    @abstractmethod
    def filter_examples(self, examples: Task) -> Task:
        raise NotImplementedError()

    @abstractmethod
    def process_output(self, nn_output):
        raise NotImplementedError()

    @abstractmethod
    def update_score(self, current_cand: typing.Union[Clause, Recursion, Body], example,
                     current_score_vector, new_score_vector):
        raise NotImplementedError()

    def get_best_primitives(
            self, examples: Task, current_cand: typing.Union[Clause, Recursion, Body]
    ) -> typing.Sequence[typing.Union[Clause, Body, Procedure]]:
        scores = [0] * 22

        # Filter examples (e.g. only use positive/negative examples)
        # examples = self.filter_examples(examples)
        pos,neg = examples.get_examples()
        # TODO nudat ik deze warning bekijk, klopt dit?
        # Calculate nn output for each example
        for example in pos:
            # Update output
            nn_output = self.model.predict(get_nn_input_data(current_cand, example, self.current_primitives.tolist()))[
                0]
            nn_output = self.process_output(nn_output)

            # Update score vector
            scores = self.update_score(current_cand, example, scores, nn_output)

        for example in neg:
            # Update output
            nn_output = self.model.predict(get_nn_input_data(current_cand, example, self.current_primitives.tolist()))[
                0]
            nn_output = self.process_output(nn_output)

            # Update score vector
            scores = self.update_score(current_cand, example, scores, -0.2*nn_output)

        # Return x best primitives
        indices = numpy.argpartition(scores, -self.amount_chosen_from_nn)[-self.amount_chosen_from_nn:]

        # TODO beste x volgens ordening of gwn zoals nu, beste x random volgorde?
        return self.current_primitives[indices]

    def process_expansions(self, current_cand: typing.Union[Clause, Procedure], examples: Task,
                           exps: typing.Sequence[Clause], primitives, hypothesis_space: TopDownHypothesisSpace):
        # Encode current candidate to list
        encoded_current_cand = clause_to_list(current_cand, self.current_primitives.tolist())

        # eliminate every clause with more body literals than allowed
        exps = [cl for cl in exps if len(cl) <= self._max_body_literals]

        # check if every clause has solutions
        exps = [(cl, self._solver.has_solution(*cl.get_body().get_literals())) for cl in exps]
        new_exps = []

        for ind in range(len(exps)):
            if exps[ind][1]:
                current_exp = exps[ind][0]
                encoded_exp = clause_to_list(current_exp, self.current_primitives.tolist())
                prim_index = find_difference(encoded_current_cand, encoded_exp)
                if (not prim_index and self.rules != 0) or self.current_primitives[prim_index] in primitives:
                    # keep it if it has solutions and if it has an allowed primitive
                    pos, neg = self.evaluate_distinct(examples, current_exp)
                    new_exp = Triplet(current_exp, pos, neg)
                    new_exps.append(new_exp)

                    # TODO miss beter op moment daje hem uit pool neemt (minder berekeningen, stel je overloopt ze
                    #  nie allemaal), idk if possible though
                    self.set_example_weights(current_cand, current_exp, examples)
            else:
                # remove from hypothesis space if it does not
                hypothesis_space.remove(exps[ind][0])

        new_exps = sorted(new_exps, key=cmp_to_key(Triplet.comparator), reverse=True)[:self.filter_amount]
        new_exps_real = []

        for triplet in new_exps:
            new_exps_real.append(triplet.get_tuple())

        print(new_exps_real)
        return new_exps_real

    def evaluate_distinct(self, examples: Task, clause: Clause) -> typing.Tuple[int, int]:
        covered = self._execute_program(examples, clause)
        pos, neg = examples.get_examples()

        covered_pos = pos.intersection(covered)
        covered_neg = neg.intersection(covered)

        return len(covered_pos), len(covered_neg)

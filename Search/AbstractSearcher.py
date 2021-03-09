import string
import typing
from abc import ABC, abstractmethod

import numpy
from pylo.language.commons import c_functor, c_pred, Structure, List

from loreleai.learning.hypothesis_space import TopDownHypothesisSpace
from loreleai.learning.task import Task, Knowledge
from loreleai.reasoning.lp.prolog import Prolog

from loreleai.language.lp import (
    Predicate,
    Clause,
    Procedure,
    Atom,
    Body,
    Recursion,
)


class AbstractSearcher(ABC):

    def __init__(self, solver_instance: Prolog, primitives):
        self._solver = solver_instance
        self.current_primitives = numpy.array(primitives)
        self._candidate_pool = []
        self.example_weights = {}
        s = c_functor("s", 2)

        self._solver.asserta(c_pred("test_task", 1)(Structure(s, [List([]), List([])])))

    def _assert_knowledge(self, knowledge: Knowledge):
        """
        Assert knowledge into Prolog engine
        """
        facts = knowledge.get_atoms()
        for f_ind in range(len(facts)):
            self._solver.assertz(facts[f_ind])

        clauses = knowledge.get_clauses()
        for cl_ind in range(len(clauses)):
            self._solver.assertz(clauses[cl_ind])

    def _execute_program(self, examples: Task, clause: Clause) -> typing.Sequence[Atom]:
        """
        Evaluates a clause using the Prolog engine and background knowledge

        Returns a set of atoms that the clause covers
        """
        if len(clause.get_body().get_literals()) == 0:
            return []
        else:
            self._solver.asserta(clause)
            covered_examples = []
            pos, neg = examples.get_examples()
            total_examples = pos.union(neg)
            for example in total_examples:
                if self._solver.has_solution(example):
                    covered_examples.append(example)
            self._solver.retract(clause)

            # head_predicate = clause.get_head().get_predicate()
            # head_variables = clause.get_head_variables()
            #
            # sols = self._solver.query(*clause.get_body().get_literals())
            #
            # sols = [head_predicate(*[s[v] for v in head_variables]) for s in sols]

            return covered_examples

    @abstractmethod
    def initialise_pool(self):
        """
        Creates an empty pool of candidates
        """
        raise NotImplementedError()

    @abstractmethod
    def get_from_pool(self) -> Clause:
        """
        Gets a single clause from the pool
        """
        raise NotImplementedError()

    @abstractmethod
    def put_into_pool(self, candidates: typing.Union[Clause, Procedure, typing.Sequence]) -> None:
        """
        Inserts a clause/a set of clauses into the pool
        """
        raise NotImplementedError()

    @abstractmethod
    def evaluate(self, examples: Task, clause: Clause) -> typing.Union[int, float]:
        """
        Evaluates a clause  of a task

        Returns a number (the higher the better)
        """
        raise NotImplementedError()

    @abstractmethod
    def stop_inner_search(self, eval: typing.Union[int, float], examples: Task, clause: Clause) -> bool:
        """
        Returns true if the search for a single clause should be stopped
        """
        raise NotImplementedError()

    @abstractmethod
    def process_expansions(self, current_cand: typing.Union[Clause, Procedure], examples: Task,
                           exps: typing.Sequence[Clause], primitives, hypothesis_space: TopDownHypothesisSpace) \
            -> typing.Sequence[Clause]:
        """
        Processes the expansions of a clause
        It can be used to eliminate useless expansions (e.g., the one that have no solution, ...)

        Returns a filtered set of candidates
        """
        raise NotImplementedError()

    @abstractmethod
    def get_best_primitives(self, examples: Task, node: typing.Union[Clause, Recursion, Body]):
        raise NotImplementedError()

    @abstractmethod
    def set_example_weights(self, previous_cand: typing.Union[Clause, Procedure],
                            current_cand: typing.Union[Clause, Procedure], examples: Task):
        raise NotImplementedError()

    @abstractmethod
    def get_initial_weights(self, examples: Task) -> dict:
        raise NotImplementedError()

    def _learn_one_clause(self, examples: Task, hypothesis_space: TopDownHypothesisSpace) -> Clause:
        """
        Learns a single clause

        Returns a clause
        """
        # reset the search space
        hypothesis_space.reset_pointer()

        # empty the pool just in case
        self.initialise_pool()

        # put initial candidates into the pool
        self.put_into_pool(hypothesis_space.get_current_candidate())
        current_cand = None
        first = True
        score = -100

        while current_cand is None or (
                len(self._candidate_pool) > 0 and not self.stop_inner_search(score, examples, current_cand)):
            # get first candidate from the pool
            current_cand = self.get_from_pool()

            if first:
                self.example_weights[current_cand] = self.get_initial_weights(examples)
                first = False

            # expand the candidate and get possible expansions
            _ = hypothesis_space.expand(current_cand)
            exps = hypothesis_space.get_successors_of(current_cand)

            # Get scores for primitives using current candidate and each example
            primitives = self.get_best_primitives(examples, current_cand)
            exps = self.process_expansions(current_cand, examples, exps, primitives, hypothesis_space)

            # add into pool
            self.put_into_pool(exps)
            score = self.evaluate(examples, current_cand)
            print(len(current_cand))
            print(current_cand)


        return current_cand

    def learn(self, examples: Task, background_location: string, hypothesis_space: TopDownHypothesisSpace):
        """
        General learning loop
        """

        self._solver.consult(background_location)
        final_program = []
        examples_to_use = examples
        pos, _ = examples_to_use.get_examples()

        while len(final_program) == 0 or len(pos) > 0:
            # learn a single clause
            cl = self._learn_one_clause(examples_to_use, hypothesis_space)
            final_program.append(cl)

            # update covered positive examples
            covered = self._execute_program(examples, cl)
            pos, neg = examples_to_use.get_examples()
            pos = pos.difference(covered)


            examples_to_use = Task(pos, neg)
            # Reset example weights
            self.example_weights = {}
            print(final_program)
            print(covered)

        return final_program

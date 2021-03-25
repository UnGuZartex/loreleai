from functools import reduce

from loreleai.language.lp import Body, Atom, Not, Predicate
from .utilities import are_variables_connected, literal_exist_g1_same_variables, get_recursive_calls_amount, \
    duplicated_var_set_exists, only_1_pred_exists_for_1_var, new_input_exists, not_previous_output_as_input_exists, \
    unexplained_last_var_exists, endless_recursion_exists, strict_unexplained_last_var_exists

"""
It contains the functions used to prune the search space
"""


def has_singleton_vars(head: Atom, body: Body) -> bool:
    """
    Returns True is the clause has a singleton variable (appears only once)
    """
    if len(body) == 0:
        return False

    vars = {}
    head_vars = head.get_variables()
    for ind in range(len(head_vars)):
        if head_vars[ind] not in vars:
            vars[head_vars[ind]] = head_vars.count(head_vars[ind])

    bvars = body.get_variables()
    body_vars_flat = reduce(lambda x, y: x + y, [x.get_variables() for x in body.get_literals()], [])
    for ind in range(len(bvars)):
        if bvars[ind] in vars:
            vars[bvars[ind]] += body_vars_flat.count(bvars[ind])
        else:
            vars[bvars[ind]] = body_vars_flat.count(bvars[ind])

    return True if any([k for k, v in vars.items() if v == 1]) else False


def max_var(head: Atom, body: Body, max_count: int) -> bool:
    """
    Return True if there are no more than max_count variables in the clause
    """
    vars = body.get_variables()
    for v in head.get_variables():
        if v not in vars:
            vars += [v]
    return True if len(vars) <= max_count else False


def connected_body(head: Atom, body: Body) -> bool:
    """
    Returns True if variables in the body cannot be partitioned in two non-overlapping sets
    """
    if len(body) == 0:
        return True
    return are_variables_connected([x.get_atom() if isinstance(x, Not) else x for x in body.get_literals()])


def connected_clause(head: Atom, body: Body) -> bool:
    """
    Returns True is the variables in the clause cannot be partitioned in two non-overlapping sets
    """
    if len(body) == 0:
        return True
    return are_variables_connected([x.get_atom() if isinstance(x, Not) else x for x in body.get_literals() + [head]])


def negation_at_the_end(head: Atom, body: Body) -> bool:
    """
    Returns True is negations appear after all positive literals
    """
    pos_location = -1
    neg_location = -1
    lits = body.get_literals()

    for ind in range(len(lits)):
        if isinstance(lits[ind], Atom):
            pos_location = ind
        elif neg_location < 0:
            neg_location = ind

    return False if (-1 < neg_location < pos_location) else True


def max_pred_occurrences(head: Atom, body: Body, pred: Predicate, max_occurrence: int) -> bool:
    """
    Returns True if the predicate pred does not appear more than max_occurrence times in the clause
    """
    preds = [x for x in body.get_literals() if x.get_predicate() == pred]

    return len(preds) <= max_occurrence


def has_duplicated_literal(head: Atom, body: Body) -> bool:
    """
    Returns True if there are duplicated literals in the body
    """
    return len(body) != len(set(body.get_literals()))


def has_double_recursion(head: Atom, body: Body) -> bool:
    """
    Returns True if a recursive call is called twice in the clause
    """
    return get_recursive_calls_amount(head, body) >= 2


def has_g1_same_vars_in_literal(head: Atom, body: Body) -> bool:
    """
    Returns True if there exists a literal with all same vars
    """
    return literal_exist_g1_same_variables([x.get_atom() if isinstance(x, Not) else x for x in body.get_literals()])


def has_duplicated_var_set(head: Atom, body: Body) -> bool:
    """
    Returns True if there exists a variable set that is also used in other literals in the body
    """
    return duplicated_var_set_exists([x.get_atom() if isinstance(x, Not) else x for x in body.get_literals()])


def only_1_pred_for_1_var(head: Atom, body: Body) -> bool:
    return only_1_pred_exists_for_1_var([x.get_atom() if isinstance(x, Not) else x for x in body.get_literals()])


def has_unexplained_last_var(head: Atom, body: Body) -> bool:
    return unexplained_last_var_exists([x.get_atom() if isinstance(x, Not) else x for x in body.get_literals()])


def has_unexplained_last_var_strict(head: Atom, body: Body) -> bool:
    return strict_unexplained_last_var_exists([x.get_atom() if isinstance(x, Not) else x for x in body.get_literals()])


def has_new_input(head: Atom, body: Body) -> bool:
    atom_list = [x.get_atom() if isinstance(x, Not) else x for x in body.get_literals()]
    atom_list.insert(0, head)

    return new_input_exists(atom_list)


def has_not_previous_output_as_input(head: Atom, body: Body) -> bool:
    atom_list = [x.get_atom() if isinstance(x, Not) else x for x in body.get_literals()]
    atom_list.insert(0, head)

    return not_previous_output_as_input_exists(atom_list)


def has_endless_recursion(head: Atom, body: Body) -> bool:
    return endless_recursion_exists(head, body)


def head_first(head: Atom, body: Body) -> bool:
    return len(set(body.get_literals()[0].get_variables()).intersection(set(head.get_variables()))) != 0

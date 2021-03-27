from filereaders.taskreader import readPositiveOfType
from loreleai.language.lp import c_pred, c_functor, c_var, List
from loreleai.reasoning.lp.prolog import SWIProlog

# Test for the given background knowledge
pl = SWIProlog()
pl.consult("../inputfiles/StringTransformations_BackgroundKnowledge.pl")
test = readPositiveOfType("../inputfiles/StringTransformationProblems", "test_task")

# Basic variables
test_task = c_pred("test_task", 1)
A = c_var("A")
B = c_var("B")

# one of the examples: test_task(s(['o','x','1',' ','3','c','p'],['O','X','1','3','C','P']))
# Everything in this set starts with lowercase 'o' in the input and uppercase 'O' in output, like the example above
# One example in this set is used to test if it's covered by the clauses below.
tex = test.get("b113").pop()


# We test whether the example starts without a space, this should be true
not_space = c_pred("not_space", 1)  # not_space(A):- \+is_space(A).
cl = test_task(A) <= not_space(A)# We test whether the facts are loaded in correctly
pl.asserta(cl)
sol = pl.has_solution(tex)  # Returns true, good
print(sol)
pl.retract(cl)


# We test whether the facts are loaded in correctly
X = c_var("X")
is_lowercase_aux = c_pred("is_lowercase_aux", 1)
query = is_lowercase_aux(X)
rv = pl.query(query)
print(rv)  # Prints all lowercase letters, good

# We test whether the example starts with a lowercase letter in the input, this should be true
is_lowercase = c_pred("is_lowercase", 1)  # is_lowercase(s([H|_],_)):-is_lowercase_aux(H).
cl = test_task(A) <= is_lowercase(A)
pl.asserta(cl)
print(tex)
sol = pl.has_solution(tex)  # Returns false, not good (?)
print(sol)
pl.retract(cl)


# We test whether the facts are loaded in correctly
X = c_var("X")
Y = c_var("Y")
convert_case = c_pred("convert_case", 2)
query = convert_case(X, Y)
rv = pl.query(query)
print(rv)  # Prints letter pairs, good

# We test whether the example starts with a lowercase letter in the input & uppercase in the output, this should be true
mk_uppercase = c_pred("mk_uppercase", 2)  # mk_uppercase(s([H1|Ta],[H2|Tb]),s(Ta,Tb)):- convert_case(H2,H1).
cl = test_task(A) <= mk_uppercase(A, B)
pl.asserta(cl)
print(tex)
sol = pl.has_solution(tex)  # Returns false, not good (?)
print(sol)
pl.retract(cl)
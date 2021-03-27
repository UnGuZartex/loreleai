from filereaders.taskreader import readPositiveOfType
from loreleai.language.lp import c_pred, c_functor, c_var, List
from loreleai.reasoning.lp.prolog import SWIProlog

pl = SWIProlog()

p = c_pred("p", 2)
f = c_functor("t", 3)
f1 = p("a", "b")

pl.assertz(f1)

X = c_var("X")
Y = c_var("Y")

query = p(X, Y)

r = pl.has_solution(query)
print("has solution", r)

rv = pl.query(query)
print("all solutions", rv)

f2 = p("a", "c")
pl.assertz(f2)

rv = pl.query(query)
print("all solutions after adding f2", rv)

func1 = f(1, 2, 3)
f3 = p(func1, "b")
pl.assertz(f3)

rv = pl.query(query)
print("all solutions after adding structure", rv)

l = List([1, 2, 3, 4, 5])

member = c_pred("member", 2)

query2 = member(X, l)

rv = pl.query(query2)
print("all solutions to list membership ", rv)

r = c_pred("r", 2)
f4 = r("a", l)
f5 = r("a", "b")

pl.asserta(f4)
pl.asserta(f5)

query3 = r(X, Y)

rv = pl.query(query3)
print("all solutions after adding list ", rv)


# Test for the given background knowledge
pl = SWIProlog()
pl.consult("../inputfiles/StringTransformations_BackgroundKnowledge.pl")
test = readPositiveOfType("../inputfiles/StringTransformationProblems", "test_task")

test_task = c_pred("test_task", 1)
is_lowercase = c_pred("is_lowercase", 1)  # is_lowercase(s([H|_],_)):-is_lowercase_aux(H).
not_space = c_pred("not_space", 1)  # not_space(A):- \+is_space(A).
A = c_var("X")

# onr of the examples: test_task(s(['o','x','1',' ','3','c','p'],['O','X','1','3','C','P']))
# Everything in this set starts with lowercase 'o'
tex = test.get("b113").pop()

cl = test_task(A) <= is_lowercase(A)
pl.asserta(cl)
print(tex)
sol = pl.has_solution(tex)  # Returns false, not good (?)
print(sol)
pl.retract(cl)

cl = test_task(A) <= not_space(A)
pl.asserta(cl)
sol = pl.has_solution(tex)  # Returns true, good
print(sol)
pl.retract(cl)


rv = pl.query(query2)


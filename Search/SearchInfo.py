import random

import numpy
from pylo.language.commons import c_pred
from tensorflow import keras

from filereaders.knowledgereader import createKnowledge
from filereaders.taskreader import readPositiveOfType
from loreleai.learning import plain_extension, TopDownHypothesisSpace, has_singleton_vars, has_duplicated_literal
from utility.datapreprocessor import get_nn_input_data

# Om de primitives en examples op te vragen:

chosen_pred = "b45"
_, predicates = createKnowledge("../inputfiles/StringTransformations_BackgroundKnowledge.pl",
                                             chosen_pred)
test = readPositiveOfType("../inputfiles/StringTransformationProblems", "test_task")

totalextension = []
filtered_predicates = []
for predicate in predicates:
    if predicate.name not in ["s", chosen_pred] and predicate not in filtered_predicates:
        # Deze lijn is als je een hypothesis space gebruikt (wss wel dus)
        totalextension.append(lambda x, predicate=predicate: plain_extension(x, predicate, connected_clauses=True))
        filtered_predicates.append(predicate)

# create the hypothesis space, ge kan recursion nog aanzetten hier ofcourse
hs = TopDownHypothesisSpace(primitives=totalextension,
                            head_constructor=c_pred("train_task", 1),
                            expansion_hooks_reject=[lambda x, y: has_singleton_vars(x, y),
                                                    lambda x, y: has_duplicated_literal(x, y)])


# Neural network kan je inladen als volgt:

model = keras.models.load_model("../utility/Saved_model", compile=True)
print(model.summary())

# Een prediction met de neural network kan je als volgt doen:

output = model.predict(get_nn_input_data(hs.get_current_candidate()[0], random.sample(test["b45"],1)[0], filtered_predicates))

print(output[0])

# Code om de 3 grootste te krijgen uit de output (niet in gesorteerde volgorde)
ind = numpy.argpartition(output[0], -3)[-3:]
print(ind)

numpy_predicates = numpy.array(filtered_predicates)
print(numpy_predicates[ind])

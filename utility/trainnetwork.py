import numpy
from tensorflow import keras
from tensorflow.keras import layers
import tensorflow as tf

print(tf.config.list_physical_devices())

input_model = keras.Input(shape=(120,), dtype='int32')
embedded_input = layers.Embedding(128, 64, input_length=120)(input_model)
encoded_input = layers.LSTM(64)(embedded_input)

output_model = keras.Input(shape=(120,), dtype='int32')
embedded_output = layers.Embedding(128, 64, input_length=120)(output_model)
encoded_output = layers.LSTM(64)(embedded_output)

clause_input = keras.Input(shape=(45,), dtype='float32')

merged = keras.layers.concatenate([clause_input, encoded_input, encoded_output])
hidden = keras.layers.Dense(100, activation='relu')(merged)
hidden2 = keras.layers.Dense(100, activation='relu')(hidden)
output = keras.layers.Dense(22, activation='sigmoid')(hidden2)

model = keras.Model(inputs=[clause_input, input_model, output_model], outputs=output)

model.compile(optimizer='adam',
    loss='mean_absolute_error',
    metrics=['mean_absolute_error'])

print("fetching data")


def fetch_data():
    x_clause = []
    x_input = []
    x_output = []
    y = []
    with open("processeddata_average.csv", "r") as f:
        for line in f.readlines():
            line = line.replace("\n", "")
            list_of_floats = [float(item) for item in line.split(",")]
            y.append(list_of_floats[-22:])
            x_clause.append(list_of_floats[:45])
            x_input.append(list_of_floats[45:165])
            x_output.append(list_of_floats[165:-22])

    x_clause = numpy.array(x_clause)
    x_input = numpy.array(x_input)
    x_output = numpy.array(x_output)
    x = [x_clause, x_input, x_output]
    y = numpy.array(y)
    print(x)
    return x,y


x_train, y_train = fetch_data()
print("training model")
model.fit(x_train, y_train, batch_size=100, epochs=30)

model.save("Saved_model")

print(model.summary())


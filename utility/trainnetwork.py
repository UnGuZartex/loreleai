from tensorflow import keras
from tensorflow.keras import layers
import tensorflow as tf

print(tf.config.list_physical_devices())

input_model = keras.Input(shape=(120,), dtype='int32')
embedded_input = layers.Embedding(300, 256)(input_model)
encoded_input = layers.LSTM(256)(embedded_input)

output_model = keras.Input(shape=(120,), dtype='int32')
embedded_output = layers.Embedding(300, 256)(output_model)
encoded_output = layers.LSTM(256)(embedded_output)

clause_input = keras.Input(shape=(24,), dtype='float32')

merged = keras.layers.concatenate([clause_input, encoded_input, encoded_output])
hidden = keras.layers.Dense(100, activation='relu')(merged)
output = keras.layers.Dense(22, activation='sigmoid')(hidden)

model = keras.Model(inputs=[clause_input, input_model, output_model], outputs=output)

model.save("Saved_model")

print(model.summary())

model = ""
model = keras.models.load_model("Saved_model")
print(model.summary())

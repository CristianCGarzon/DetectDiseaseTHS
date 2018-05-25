import numpy as np

np.random.seed(7)
from ths.utils.sentences import SentenceToEmbedding

from keras.models import Model
from keras.layers import Dense, Input, Dropout, LSTM, Activation, Bidirectional, BatchNormalization, GRU, Conv1D, \
    Conv2D, MaxPooling2D, Flatten, Reshape, GlobalAveragePooling1D, GlobalMaxPooling1D, AveragePooling1D, AveragePooling2D, Concatenate
from keras.layers.embeddings import Embedding


class  TweetSentiment2DCNN2Channel:
    def __init__(self, max_sentence_len, embedding_builder):
        self.max_sentence_len = max_sentence_len
        self.embedding_builder = embedding_builder
        self.model = None

    def build(self, first_dropout=0.0, padding='same', filters=4, kernel_size=(1,1), strides=(1,1), activation='relu',
              dense_units=64, second_dropout=0.0):

        # Input Layer 1 - tweet in right order
        sentence_input = Input(shape=(self.max_sentence_len,), name="INPUT_1")
        reverse_sentence_input = Input(shape=(self.max_sentence_len,), name="INPUT_2")
        # Embedding layer
        embeddings_layer = self.pretrained_embedding_layer()
        embeddings1 = embeddings_layer(sentence_input)
        embeddings2 = embeddings_layer(reverse_sentence_input)

        # Reshape
        embeddings1= Reshape((self.max_sentence_len, self.embedding_builder.get_dimensions(), 1))(embeddings1)
        embeddings2= Reshape((self.max_sentence_len, self.embedding_builder.get_dimensions(), 1))(embeddings2)

        #stack both input to make it a 2 chanell input
        concat_embeddings = Concatenate(axis = -1)([embeddings1, embeddings2])
        print("concat_embeddings: ", concat_embeddings)
        # Reshape with channels
        #X = Reshape((self.max_sentence_len, self.embedding_builder.get_dimensions(), 1))(embeddings)

        # First convolutional layer
        kernel_width = self.embedding_builder.get_dimensions()
        kernel_height = 3
        kernel_size = (kernel_height, kernel_width)
        X = Conv2D(filters=20, kernel_size=kernel_size, strides=(1, 1), padding=padding, activation=activation,
                   name="CONV2D_1")(concat_embeddings)
        #X  = Conv2D(filters = 66, kernel_size = (kernel_height+2, 1),  strides=(1, 1), padding='same', activation=activation,
        #           name="CONV2D_2")(X)
        #MAX pooling
        pool_height =  self.max_sentence_len - kernel_height + 1  # assumes zero padding and stride of 1
        pool_size = (pool_height, 1)
        X = AveragePooling2D(pool_size=pool_size, name = "MAXPOOL_1")(X)

        #Flatten
        X = Flatten()(X)

        # # First dense layer
        dense_units = 128
        X = Dense(units=int(dense_units/2), activation='relu', name="DENSE_1")(X)
        X = Dropout(second_dropout, name="DROPOUT_1")(X)

        # # Second dense layer
        X = Dense(units=dense_units, activation='relu', name="DENSE_2")(X)
        X = Dropout(second_dropout, name="DROPOUT_2")(X)
        #
        # # Third layer
        X = Dense(units=int(dense_units/2), activation='relu', name="DENSE_3")(X)
        X = Dropout(second_dropout, name="DROPOUT_3")(X)

        # Final layer
        X = Dense(1, activation= "sigmoid", name="FINAL_SIGMOID")(X)
        # create the model
        self.model = Model(input=[sentence_input, reverse_sentence_input] , output=X)

    def pretrained_embedding_layer(self):
        # create Keras embedding layer
        word_to_idx, idx_to_word, word_embeddings = self.embedding_builder.read_embedding()
        #vocabulary_len = len(word_to_idx) + 1
        vocabulary_len = len(word_to_idx)
        emb_dimension = self.embedding_builder.get_dimensions()
        # get the matrix for the sentences
        embedding_matrix = word_embeddings
        #embedding_matrix = np.vstack([word_embeddings, np.zeros((vocabulary_len,))])

        # embedding layer
        embedding_layer = Embedding(input_dim=vocabulary_len, output_dim=emb_dimension, trainable=False, name="EMBEDDING")
        embedding_layer.build((None,))
        embedding_layer.set_weights([embedding_matrix])
        return embedding_layer

    def summary(self):
        self.model.summary()

    def compile(self, loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy']):
        self.model.compile(loss=loss, optimizer=optimizer, metrics=metrics)

    def fit(self, X, Y, epochs = 50, batch_size = 32, shuffle=True, callbacks=None, validation_split=0.0, class_weight=None):
        return self.model.fit(X, Y, epochs=epochs, batch_size=batch_size, shuffle=shuffle, callbacks=callbacks,
                       validation_split=validation_split, class_weight=class_weight)

    def evaluate(self, X_test, Y_test):
        return self.model.evaluate(X_test, Y_test)

    def predict(self, X):
        return self.model.predict(X)

    def get_sentiment(self, prediction):
        return np.argmax(prediction)

    #def sentiment_string(self, sentiment):
    #    return self.sentiment_map[sentiment]

    def save_model(self, json_filename, h5_filename):
        json_model = self.model.to_json()
        with open(json_filename, "w") as json_file:
            json_file.write(json_model)
        self.model.save_weights(h5_filename)
        return
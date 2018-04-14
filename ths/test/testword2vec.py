from ths.nn.embedding.word2vec import SkipGrams, Word2VecNegSam, Word2VecValidationCallback
import numpy as np
from ths.utils.datasets import TweetDataSetGenerator

def main():
    T  = TweetDataSetGenerator("data/cleantextlabels2.csv")
    data, count, dictionary, reverse_dictionary = T.get_dataset()
    S = SkipGrams(text_data=data, dictionary_size=10000)
    targets, contexts, labels = S.build()
    print("targets: ", targets[:10])
    print("contexts: ", contexts[:10])
    print("labels: ", labels[:10])

    print("Create Word2Vect")
    W2V = Word2VecNegSam(len(dictionary), 100)
    print("Build Word2Vect")
    W2V.build()
    print("Summary")
    W2V.summary()
    print("Compile the model")
    W2V.compile()
    print("Get Validation model")
    validation_model = W2V.get_validation_model()
    print("Build callback")
    C = Word2VecValidationCallback(reverse_dictionary=reverse_dictionary, validation_model = validation_model,
                                   valid_size=16, valid_window=100, top_k=8)
    epochs = 1000000
    print("train W2V for %s epochs " % epochs)
    embedding= W2V.train(targets, contexts, labels, epochs=epochs, callback=None)
    print("embedding len: ", len(embedding))
    print(embedding[0])
    print("shape: ", embedding[0].shape)
    print("type(embedding[0]): ", type(embedding[0]))
    for i in range(10):
        print("word i: ", reverse_dictionary[i])
        print("embedding: ", embedding[0][i])
        print(" ")

    i = dictionary['shit']
    j = dictionary['crap']
    v1 = embedding[0][i]
    v2 = embedding[0][j]
    print("v1-v2", v1 - v2)

    with open("trained/embedding1.txt", "w") as f:
        for word, idx in dictionary:
            e = embedding[0][i]

    print("Done")

if __name__ == "__main__":
    main()
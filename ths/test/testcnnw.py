from ths.nn.sequences.processcnnw import ProcessTweetsCNN

def main():
    print("Working:")
    #P = ProcessTweetsWord2VecOnePass2DCNNv2_1("data/cleantextlabels3.csv", "trained/embedding3.csv")
    P = ProcessTweetsCNN("data/cleantextlabels6.csv", "data/glove.6B.50d.txt")
    #P = ProcessTweetsWord2VecTwoPassLSTMv2_1("data/cleantextlabels4.csv", "trained/embedding3-50d.csv")

    #Bueno el model12cnnv2
    # Excelente el de modellstmatt1 con attention
    # El mejor fue modellstmatt2 con attention
    # also good modellstmatt3
    # el 4 con dropout
    P.process("trained/modelcnnincepw1.json", "trained/modelcnnincepw1.h5", plot=False, epochs=80)
#joderme
if __name__ == "__main__":
    main()
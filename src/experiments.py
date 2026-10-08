import pickle
from markov import train, perplexity

with open("cache/corpora.pkl", "rb") as f:
    data = pickle.load(f)

model_nes = train(data['mel'], 5)

print("E1: perplexity on the NES test split")
for each_n in range(0, 6):
    pp = perplexity(model_nes, data['mel_test'], each_n)
    print(f"n = {each_n}: {pp:.2f}")
import numpy as np
import pickle
from markov import train, perplexity, corpus_text, longest_copy
from generate import generate_melody
from representation import intervals

with open("cache/corpora.pkl", "rb") as f:
    data = pickle.load(f)

model_nes = train(data['mel'], 5)
model_js = train(data['js'], 5)
models = {'nesmdb': model_nes, 'jsmel': model_js}
nesmdb_text = corpus_text(data['mel'])
config = {'lambd': 0.0, 'tonic': 62, 'scale': 'yo', 'melody_range': (60, 84)}

print("E1: longest copy vs NES train (lambda = 0, 10 seeds, 64 notes)")
for each_n in range(1, 6):
    config['order'] = each_n
    copies = []
    for each_seed in range(1, 11):
        rand_num = np.random.default_rng(each_seed)
        mel = generate_melody(64, models, config, rand_num)
        copies.append(longest_copy(intervals(mel), nesmdb_text))
    print(f"n = {each_n}: mean copy = {np.mean(copies):.1f}, max = {max(copies)}")

print("E1: perplexity on the NES test split")
for each_n in range(0, 6):
    pp = perplexity(model_nes, data['mel_test'], each_n)
    print(f"n = {each_n}: {pp:.2f}")
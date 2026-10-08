import pickle
import numpy as np

from generate import generate_melody
from markov import corpus_text, longest_copy, perplexity, train
from representation import intervals

with open("cache/corpora.pkl", "rb") as f:
    data = pickle.load(f)

model_nes = train(data["mel"], 5)
model_js = train(data["js"], 5)
models = {"nesmdb": model_nes, "jsmel": model_js}
nesmdb_text = corpus_text(data["mel"])

config = {
    "lambd": 0.0,
    "tonic": 62,
    "scale": "yo",
    "melody_range": (60, 84),
}

print("E1: longest copy vs NES train (lambda = 0, 10 seeds, 64 notes)")
for n in range(1, 6):
    config["order"] = n
    copies = []
    for seed in range(1, 11):
        rng = np.random.default_rng(seed)
        mel = generate_melody(64, models, config, rng)
        copies.append(longest_copy(intervals(mel), nesmdb_text))
    print(f"n = {n}: mean copy = {np.mean(copies):.2f}, max = {max(copies)}")

print("\nE1 references: longest copy of real NES test melodies vs train (63 intervals)")
ref_copies = []
for seq in data["mel_test"]:
    if len(seq) >= 63:
        ref_copies.append(longest_copy(seq[:63], nesmdb_text))
print(f"Count: {len(ref_copies)}")
print(f"Mean: {np.mean(ref_copies):.2f}")
print(f"Max: {max(ref_copies)}")

print("\nE1: perplexity on the NES test split")
for n in range(0, 6):
    pp = perplexity(model_nes, data["mel_test"], n)
    print(f"n = {n}: {pp:.2f}")
import pickle
import numpy as np

from generate import generate_melody, generate_song
from markov import corpus_text, longest_copy, perplexity, train
from representation import intervals
from nesmdb_data import vertical_intervals
from evaluation import interval_histogram, japaneseness, coherence

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

model_v = train(data["vert"], 2)
h_nes = interval_histogram(data["mel"])
h_js = interval_histogram(data["js"])
js_text = corpus_text(data["js"])
song_config = {'order': 3, 'tonic': 62, 'scale': 'yo', 'melody_range': 
               (60, 84),'bass_range': (36, 60), 'bass_order': 2, 
               'bars_per_section': 4,'bpm': 120, 'seed': 7, 
               'form': 'AABA'}

print("\nE2: effect of lambda (n = 3, 10 seeds)")
for each_lambda in [0.0, 0.25, 0.5, 0.75, 1.0]:
    song_config["lambd"] = each_lambda
    j_val = [] 
    coh_val = [] 
    copy_nes = [] 
    copy_js = []
    rep = []
    size = []

    for each_seed in range(1, 11):
        song_config["seed"] = each_seed
        song = generate_song(models, model_v, song_config)
        pitches = []
        for note in song["melody"]:
            pitches.append(note[2])
        ivs = intervals(pitches)
        h = interval_histogram([ivs])
        rep.append(h.get(0, 0))
        size.append(np.mean(np.abs(ivs)))
        j_val.append(japaneseness(h, h_nes, h_js))
        coh_val.append(coherence(vertical_intervals(song["melody"], song["bass"])))
        copy_nes.append(longest_copy(ivs, nesmdb_text))
        copy_js.append(longest_copy(ivs, js_text))
    print(f"lambda = {each_lambda:.2f}: J = {np.mean(j_val):.2f} ± "
          f"{np.std(j_val):.2f}, coherence = {np.mean(coh_val):.2f} ± "
          f"{np.std(coh_val):.2f}, copy NES = {np.mean(copy_nes):.1f}, copy "
          f"JS = {np.mean(copy_js):.1f}, rep = {np.mean(rep):.2f}, "
          f"|int| = {np.mean(size):.2f}")
print("\nE2 reference: coherence of real NES test songs")
all_v = []
for seq in data["vert_test"]:
    for v in seq:
        all_v.append(v)
        
print(f"coherence = {coherence(all_v):.2f}")
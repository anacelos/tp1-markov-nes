import nesmdb_data 
import jsmel_data

from midi_export import to_midi, save
from markov import train
from generate import generate_song
from synthesis import render, save_wav
import pickle

# Real Data
# ----------------------------------------------------------------------
mel, vert = nesmdb_data.build_corpus(nesmdb_data.NES_DIR, 'train')
if not mel:
    raise SystemExit("No NES file found. run from the repository root")
mel_test, vert_test = nesmdb_data.build_corpus(nesmdb_data.NES_DIR, 'test')
meta = jsmel_data.read_metadata(jsmel_data.META_PATH)
js = jsmel_data.build_corpus(jsmel_data.JSMEL_DIR, meta)

with open("cache/corpora.pkl", "wb") as f:
    pickle.dump({'mel': mel, 'vert': vert, 'js': js,
             'mel_test': mel_test, 'vert_test': vert_test}, f)

# Chains
# ---------------------------------------------------------------------- 
models = {'nesmdb': train(mel, 5), 'jsmel': train(js, 5)}
model_v = train(vert, 2)

# Config
# ----------------------------------------------------------------------
base = {'order': 3, 'tonic': 62, 'scale': 'yo', 'melody_range': (60, 84),
        'bass_range': (36, 60), 'bass_order': 2, 'bars_per_section': 4,
        'bpm': 120, 'seed': 7, 'form': 'AABA'}

# Songs
# ----------------------------------------------------------------------
for each_lambda in [1.0, 0.5, 0.0]:
    for each_seed in range(1, 11):
        config = dict(base) 
        config['lambd'] = each_lambda
        config['seed'] = each_seed
        song = generate_song(models, model_v, config)
        name = f"outputs/candidates/lam{each_lambda}_n3_yo_s{each_seed}"
        p_m = to_midi(song, config)
        save(p_m, config, name)
        save_wav(render(p_m), name + ".wav")
        
        print("saved:", name)
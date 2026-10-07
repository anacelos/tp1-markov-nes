import json
import pretty_midi
from markov import train
from generate import generate_song


# Functions
# ----------------------------------------------------------------------

def to_midi(song, config):
    p_m = pretty_midi.PrettyMIDI(initial_tempo = config['bpm'])
    melody = pretty_midi.Instrument(program = 80, name = 'p1')
    for each_start, each_end, each_pitch in song['melody']:
        melody.notes.append(pretty_midi.Note(velocity = 100, pitch = 
                                             each_pitch, start = each_start, 
                                             end = each_end))
    p_m.instruments.append(melody)
    bass = pretty_midi.Instrument(program = 38, name = 'tr')
    for each_start, each_end, each_pitch in song['bass']:
        bass.notes.append(pretty_midi.Note(velocity = 100, pitch = 
                                             each_pitch, start = each_start, 
                                             end = each_end))
    p_m.instruments.append(bass)
    drums = pretty_midi.Instrument(program=0, is_drum=True, name='no')    
    for each_start, each_end, each_pitch in song['drums']:
        drums.notes.append(pretty_midi.Note(velocity = 100, pitch = 
                                             each_pitch, start = each_start, 
                                             end = each_end))
    p_m.instruments.append(drums)

    return p_m

def save(p_m, config, path):
    p_m.write(path + '.mid')
    with open(path + '.json', 'w') as f:
        json.dump(config, f, indent = 2)
import pretty_midi
pretty_midi.pretty_midi.MAX_TICK = 1e10
from pathlib import Path

# Paths
NES_DIR = "data/nesmdb_midi"

# Functions
# ----------------------------------------------------------------------

def load(midi_path):
    """Return a dictionary where the key is the name and the value is
    a list of (start, end, pitch) tuples."""

    pum = pretty_midi.PrettyMIDI(midi_path)
    dictionary = {}
    for each_instrument in pum.instruments:
        if each_instrument.name == 'no':
            continue
        notes = []
        for each_note in each_instrument.notes:
            start = each_note.start
            end = each_note.end
            pitch = each_note.pitch
            dur = end - start
            if dur < 1 /60:
                continue
            else:
                notes.append((start, end, pitch))
        notes.sort()
        dictionary[each_instrument.name] = notes

    return dictionary

def mean_pitches(notes):
    """Return the mean pitch of a list of (start, end, pitch) tuples, or None 
    if the list is empty."""

    pitches = []
    for each_note in notes:
        pitches.append(each_note[2])
    if not pitches: 
        return None

    return sum(pitches) / len(pitches)

def melody_voice(voices):
    """Return the notes of the pulse voice (p1 or p2) with the highest mean 
    pitch, or an empty list."""
    
    if 'p1' in voices and voices['p1'] and 'p2' in voices and voices['p2']:
        if mean_pitches(voices['p1']) >= mean_pitches(voices['p2']):
            return voices['p1']
        else:
            return voices['p2']
    elif 'p1' in voices and voices['p1']:
        return voices['p1']
    elif 'p2' in voices and voices['p2']:
        return voices['p2']
    else:
        return []

def vertical_intervals(melody, bass):
    """Return the vertical intervals (melody − bass) at each bass onset, read 
    1/120 s after it. Bass notes with no sounding melody, or with an interval 
    outside [0, 36], are skipped."""

    v = []
    for bass_note in bass:
        time = bass_note[0] + 1/120
        found_pitch = None 
        for mel_note in melody:
            if mel_note[0] <= time < mel_note[1]:
                found_pitch = mel_note[2]
                break
        if found_pitch is None:
            continue
        interval = found_pitch - bass_note[2]
        if interval < 0 or interval > 36:
            continue
        v.append(interval)

    return v
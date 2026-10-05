import pretty_midi
pretty_midi.pretty_midi.MAX_TICK = 1e10

# Paths
# ----------------------------------------------------------------------
midi_path = "data/nesmdb_midi"

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
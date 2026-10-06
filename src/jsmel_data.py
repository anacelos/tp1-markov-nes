import pandas
import pretty_midi
from pathlib import Path
from representation import intervals

# Constants
# ----------------------------------------------------------------------
JSMEL_DIR = "data/jsmel"
META_PATH = "data/jsmel/Metadata_JSMel.xlsx"

# Functions
# ----------------------------------------------------------------------
def read_metadata(xlsx_path):
    """Return s pandas DataFrame with the contentes of the first sheet."""

    return pandas.read_excel(xlsx_path)

def melody_path(folder, song_id):
    """Return a pathlib.Path pointing to <folder>/<song_id[0]>/P_<song_id>.txt"""

    return Path(folder) / song_id[0] / ("P_" + song_id + ".txt")

def read_melody(folder, song_id):
    """Return the MIDI pitches of a JSMel melody, skipping rests."""

    pitches = []
    with open(melody_path(folder, song_id)) as f:
        for line in f: 
            name = line.strip()
            if name == "rest" or name == "":
                continue
            pitches.append(pretty_midi.note_name_to_number(name))

    return pitches

def build_corpus(folder, metadata):
    """Return the interval sequences of the JSMel melodies that have a 
    file and are not of foreign origin, and print the counters."""

    seqs = []
    total = 0
    foreign = 0
    no_file = 0
    for index, row in metadata.iterrows():
        total += 1
        song_id = row['Melody ID']
        if row['Songs of foreign origin'] == 1:
            foreign += 1
            continue
        if not melody_path(folder, song_id).exists():
            no_file += 1
            continue
        seqs.append(intervals(read_melody(folder, song_id)))
    print(f"total: {total}", f"foreign: {foreign}", f"no_file: {no_file}",
              f"used: {len(seqs)}")
    return seqs
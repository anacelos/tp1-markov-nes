# Scales
# ----------------------------------------------------------------------

SCALES = {'yo': [0, 2, 5, 7, 9],
         'in': [0, 1, 5, 7, 8],
         'major': [0, 2, 4, 5, 7, 9, 11],
         'minor': [0, 2, 3, 5, 7, 8, 10],
        }

# Functions
# ----------------------------------------------------------------------

def intervals(pitches, limit = 12):
    """Return a list with the difference between each pitch and the next."""

    difference = []
    for i in range(len(pitches) - 1):

        step = pitches[i+1] - pitches[i]
        if step > limit:
            step = limit
        elif step < -limit:
            step = -limit
        difference.append(step)
    
    return difference

def voice_range_pitches(tonic, scale, pitch_range):
    """Return the pitches that can be played."""

    degrees = SCALES[scale]
    allowed = []

    for note in range((pitch_range[0]), (pitch_range[1] + 1)):
        distance = (note - tonic) % 12
        if distance in degrees:
            allowed.append(note)
    
    return allowed

def is_consonant(interval):
    """Return True or False based in the distance between melody and bass."""

    consonant = [0, 3, 4, 7, 8, 9]
    distance = interval % 12
    if distance == 0:
        return True
    if distance in consonant:
        return True 

    return False


def pattern_to_onsets(pattern, t0, step_dur):
    """Return the times (in seconds) where the notes start."""
    
    onset = []
    for i, j  in enumerate(pattern):
        if j != '.':
            time = t0 + step_dur*i
            onset.append(time)

    return onset
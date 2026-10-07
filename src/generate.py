import numpy as np
from representation import pattern_to_onsets, voice_range_pitches
from markov import train, mix, distribution, constrain, sample

# Constants
# ----------------------------------------------------------------------
PATTERNS = {'melody': 'x.x.x.x.x.x.x.x.', 'bass': 'x...x...x...x...', 
            'drums': 'k...h...s...h...'}
DRUM_PITCHES = {'k': 36, 's': 38, 'h': 42}

# Functions
# ----------------------------------------------------------------------

def section_onsets(pattern, n_bars, t0, bpm):
    """
    Return the onset times of a voice over n_bars bars starting at t0, 
    repeating the 16-step pattern.
    """

    step_dur = 60 / bpm / 4
    bar_dur = 16 * step_dur
    onsets = []
    for each_bar in range(n_bars):
        bar_start_time = t0 + (each_bar * bar_dur)
        onsets.extend(pattern_to_onsets(pattern, bar_start_time, step_dur))

    return onsets

def generate_melody(n_notes, models, config, random_numb):
    """
    Return n_notes melody pitches: start on the tonic, draw intervals from 
    the lambda-mixed chains restricted to the scale and range, and end on a 
    tonic.
    """

    allowed_pitches = voice_range_pitches(config['tonic'], config['scale'],
                                          config['melody_range'])
    tonics = set()
    for each_pitch in allowed_pitches:
        if (each_pitch - config['tonic']) % 12 == 0:
            tonics.add(each_pitch)
    pitches = [config['tonic']]
    history = []
    for each_i in range(1, n_notes):
        current = pitches[-1]
        d_nesmdb =  distribution(models['nesmdb'], history, config['order'])
        d_jsmel = distribution(models['jsmel'], history, config['order'])
        d = mix(d_jsmel, d_nesmdb, config['lambd'])
        if each_i == n_notes - 1:
            targets = tonics
        else:
            targets = allowed_pitches
        allowed = set()
        for each_p in targets:
            if -12 <= each_p - current <= 12:
                allowed.add(each_p - current)
        d = constrain(d, allowed)
        if not d:
            interval = min(allowed, key = abs)
        else:
            interval = sample(d, random_numb)
        pitches.append(current + interval)
        history.append(interval)

    return pitches

def generate_bass(bass_onsets, mel_onsets, mel_pitches, model_v, config, 
                  random_numb):
    """
    Return the bass pitches: at each bass onset, take the sounding melody 
    pitch m, draw v from chain V restricted to the scale and bass range, 
    and play m - v.
    """

    allowed_bass = voice_range_pitches(config['tonic'], config['scale'], 
                                       config['bass_range'])
    bass = []
    history = []
    for each_t in bass_onsets:
        mel_in_t = mel_pitches[0]
        for each_onset, each_pitch in zip(mel_onsets, mel_pitches):
            if each_onset <= each_t:
                mel_in_t = each_pitch
            else:
                break
        dist = distribution(model_v, history, config['bass_order'])
        allowed = set()
        for each_bass in allowed_bass:
            if 0 <= mel_in_t - each_bass <= 36:
                allowed.add(mel_in_t - each_bass)
        dist = constrain(dist, allowed)
        if not dist:
            vert_dist = min(allowed, key =  abs)
        else:
            vert_dist = sample(dist, random_numb)
        bass.append(mel_in_t - vert_dist)
        history.append(vert_dist)

    return bass

def to_notes(onsets, pitches, end_time):
    """
    Return (start, end, pitch) notes: each note lasts until the next 
    onset, the last one until end_time.
    """

    notes = []
    for each_i in range(len(onsets)):
        start = onsets[each_i]
        if each_i + 1 < len(onsets):
            end = onsets[each_i + 1]
        else:
            end = end_time
        notes.append((start, end, pitches[each_i]))

    return notes

def generate_section(t0, models, model_v, config, random_numb):
    """
    Return one section as {'melody', 'bass', 'drums'} lists of (start, 
    end, pitch) notes, starting at t0.
    """

    n_bars = config['bars_per_section']
    bpm = config['bpm']
    step_dur = 60 / bpm / 4
    end_time = t0 + n_bars * 16 * step_dur
    mel_on = section_onsets(PATTERNS['melody'], n_bars, t0, bpm)
    bass_on = section_onsets(PATTERNS['bass'], n_bars, t0, bpm)
    mel = generate_melody(len(mel_on), models, config, random_numb)
    bass = generate_bass(bass_on, mel_on, mel, model_v, config, random_numb)
    drum_on = section_onsets(PATTERNS['drums'], n_bars, t0, bpm)
    drum_kinds = []
    for each_bar in range(n_bars):
        for each_const in PATTERNS['drums']:
            if each_const != '.':
                drum_kinds.append(each_const)
    drums = []
    for each_t, each_kind in zip(drum_on, drum_kinds):
        drums.append((each_t, each_t + step_dur, DRUM_PITCHES[each_kind])) 

    return {'melody': to_notes(mel_on, mel, end_time),
            'bass': to_notes(bass_on, bass, end_time),
            'drums': drums}

def shift(notes, dt):
    """
    Return the notes moved dt seconds later (pitches unchanged).
    """

    shifted = []
    for each_start, each_end, each_pitch in notes:
        shifted.append((each_start+dt, each_end + dt, each_pitch))

    return shifted

def generate_song(models, model_v, config):
    """
    Return the whole song as {'melody', 'bass', 'drums'} notes: generate
    sections A and B once and arrange them following config['form'].
    """

    random_numb = np.random.default_rng(config['seed'])
    A = generate_section(0.0, models, model_v, config, random_numb)
    B = generate_section(0.0, models, model_v, config, random_numb)
    step_dur = 60 / config['bpm'] / 4
    section_dur = config['bars_per_section'] * 16 * step_dur
    song = {'melody': [], 'bass': [], 'drums': []}
    for each_i , each_letter in enumerate(config['form']):
        if each_letter == 'A':
            sec = A
        else:
            sec = B
        for each_voice in song:
            song[each_voice].extend(shift(sec[each_voice], each_i * 
                                          section_dur))

    return song
import numpy as np
from representation import pattern_to_onsets, voice_range_pitches
from markov import train, mix, distribution, constrain, sample

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
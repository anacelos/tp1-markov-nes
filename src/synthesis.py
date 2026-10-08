import wave
import numpy as np
import pretty_midi

# Functions
# ----------------------------------------------------------------------

def square_wave(x):
    """
    Return a square wave.
    """

    return np.sign(np.sin(x))

def triangle_wave(x):
    """
    Return a triangle wave.
    """

    return 2 / np.pi * np.arcsin(np.sin(x))

def render(p_m, fs = 44100):
    """
    Return mono audio in [-1, 1]: melody as a square wave, bass as a 
    triangle wave (drums not rendered).
    """

    melody = p_m.instruments[0].synthesize(fs = fs, wave = square_wave)
    bass = p_m.instruments[1].synthesize(fs = fs, wave = triangle_wave)
    n = max(len(melody), len(bass))
    audio = np.zeros(n)
    audio[:len(melody)] += 0.5 * melody
    audio[:len(bass)] += 0.5 * bass
    peak = np.max(np.abs(audio))
    if peak > 0: 
        audio = audio / peak

    return audio

def save_wav(audio, path, fs=44100):
    """
    Write audio in [-1, 1] to path as a 16-bit mono WAV file.
    """
    data = (audio * 0.9 * 32767).astype(np.int16)
    with wave.open(path, 'wb') as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(fs)
        f.writeframes(data.tobytes())
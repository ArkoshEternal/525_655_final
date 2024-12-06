# File which implements the generation of bass notes for open_synth 
import numpy as np
from scipy.io.wavfile import write

# function which generates a bass note for a given fundamental frequency
def generate_bass_note(frequency, duration=1.0, sample_rate=44100):

    # Time axis
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)

    # Fundamental frequency and harmonics
    fundamental = np.sin(2 * np.pi * frequency * t)
    harmonic_2 = 0.6 * np.sin(2 * np.pi * 2 * frequency * t)
    harmonic_3 = 0.4 * np.sin(2 * np.pi * 3 * frequency * t)
    harmonic_4 = 0.2 * np.sin(2 * np.pi * 4 * frequency * t)
    
    # Combine harmonics
    waveform = fundamental + harmonic_2 + harmonic_3 + harmonic_4

    # Apply ADSR envelope
    attack_time = 0.1  # seconds
    decay_time = 0.3  # seconds
    sustain_level = 0.7
    release_time = 0.4  # seconds
    sustain_time = duration - (attack_time + decay_time + release_time)

    attack = np.linspace(0, 1, int(sample_rate * attack_time))
    decay = np.linspace(1, sustain_level, int(sample_rate * decay_time))
    sustain = np.ones(int(sample_rate * sustain_time)) * sustain_level
    release = np.linspace(sustain_level, 0, int(sample_rate * release_time))

    envelope = np.concatenate((attack, decay, sustain, release))
    envelope = np.pad(envelope, (0, len(t) - len(envelope)), 'constant')

    # Apply envelope to waveform
    waveform = waveform * envelope

    # Normalize to avoid clipping
    waveform = waveform / np.max(np.abs(waveform))

    return waveform

# function which returns the bass note for a given fundamental frequency
def generate_bass_dict(mydict):
    return_dict = {}
    # Generate the chords and return them as key value pairs 
    for key, value in mydict.items(): 
        return_dict[key] = generate_bass_note(value)
    return return_dict
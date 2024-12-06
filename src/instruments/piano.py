import numpy as np
from scipy.signal import butter, lfilter

# This is inspired by the following tutorial: 
# https://www.youtube.com/watch?v=zuvbfYvwca4
# file which implements the generation of keyboard notes for open_synth
SAMPLE_RATE = 44100 

def analog_bd_sine(frequency, duration, sample_rate=SAMPLE_RATE):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    return np.sin(2 * np.pi * frequency * t)

def apply_adsr_envelope(waveform, attack, decay, sustain_level, release, sample_rate=SAMPLE_RATE):
    total_samples = len(waveform)
    
    # Calculate envelope points
    attack_samples = int(sample_rate * attack)
    decay_samples = int(sample_rate * decay)
    release_samples = int(sample_rate * release)
    
    # Calculate the maximum possible sustain samples
    sustain_samples = total_samples - attack_samples - decay_samples - release_samples
    
    # Create the ADSR envelope
    envelope = np.ones_like(waveform)  # Start with no attack
    
    # Decay: exponential drop to sustain level
    envelope[:decay_samples] = np.linspace(1, sustain_level, decay_samples)
    
    # Sustain: constant level
    envelope[decay_samples:decay_samples + sustain_samples] = sustain_level
    
    # Release: exponential drop
    envelope[-release_samples:] = np.linspace(sustain_level, 0, release_samples)
    
    # Apply envelope to waveform
    return waveform * envelope

def apply_lowpass_filter(waveform, cutoff, sample_rate=SAMPLE_RATE):
    nyquist = 0.5 * sample_rate
    normal_cutoff = cutoff / nyquist
    b, a = butter(4, normal_cutoff, btype='low')
    return lfilter(b, a, waveform)

def apply_lfo_finetune(waveform, lfo_freq, depth, sample_rate=SAMPLE_RATE):
    t = np.linspace(0, len(waveform) / sample_rate, len(waveform), endpoint=False)
    lfo = np.sin(2 * np.pi * lfo_freq * t) * depth
    waveform = np.interp(t + lfo, t, waveform)  # Apply LFO modulation to waveform
    return waveform

def apply_tremolo(waveform, tremolo_freq, depth, sample_rate=SAMPLE_RATE):
    t = np.linspace(0, len(waveform) / sample_rate, len(waveform), endpoint=False)
    tremolo = 1 + depth * np.sin(2 * np.pi * tremolo_freq * t)  # Amplitude modulation
    return waveform * tremolo

def apply_chorus(waveform, depth=0.3, rate=0.5, sample_rate=SAMPLE_RATE):
    t = np.linspace(0, len(waveform) / sample_rate, len(waveform), endpoint=False)
    chorus_waveform = waveform.copy()
    for i in range(1, 3):  # 2 extra voices for chorus effect
        delay = int(sample_rate * (i * 0.02))  # small delay for chorus
        chorus_waveform += np.roll(waveform, delay) * (depth / i)
    
    return chorus_waveform

def generate_synth_note(frequency, duration, sample_rate=SAMPLE_RATE):    
    # Step 1: Generate the fundamental sine wave
    waveform = analog_bd_sine(frequency, duration, sample_rate)
    
    # Step 2: Apply ADSR envelope (attack, decay, sustain, release)
    waveform = apply_adsr_envelope(waveform, attack=0.0, decay=2.0, sustain_level=0.1, release=0.1, sample_rate=sample_rate)
    
    # Step 3: Apply low-pass filter (12dB per octave)
    waveform = apply_lowpass_filter(waveform, cutoff=1000, sample_rate=sample_rate)
    
    # Step 4: Apply LFO to fine-tune oscillator
    waveform = apply_lfo_finetune(waveform, lfo_freq=0.1, depth=0.02, sample_rate=sample_rate)
    
    # Step 5: Apply tremolo effect
    waveform = apply_tremolo(waveform, tremolo_freq=5.0, depth=0.5, sample_rate=sample_rate)
    
    # Step 6: Apply another low-pass filter to deharshen
    waveform = apply_lowpass_filter(waveform, cutoff=2000, sample_rate=sample_rate)
    
    # Step 7: Add chorus effect
    waveform = apply_chorus(waveform, depth=0.3, rate=0.5, sample_rate=sample_rate)
    
    # Normalize waveform to avoid clipping
    waveform = waveform / np.max(np.abs(waveform))
    
    return waveform

# Function which returns the keyboard note for a given frequency
def generate_piano_dict(mydict): 
    return_dict = {}
    # Generate the chords and return them as key value pairs 
    for key, value in mydict.items(): 
        return_dict[key] = generate_synth_note(value, 2.0, SAMPLE_RATE)
    return return_dict
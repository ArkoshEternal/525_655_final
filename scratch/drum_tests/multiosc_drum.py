import numpy as np
from scipy.io.wavfile import write
from helper import makeplots

# Constants
SAMPLE_RATE = 44100  # Standard sample rate (44.1 kHz)
DURATION = 1.0      # Total duration of the chord (seconds)

# FM Coefficients - bell
FMFreqs     = [200] # frequency of carrier oscillator
FMFreqRatio = [0.5] # ratio of modulator to carrier
CarEnv = [0, 0, 0.1, 1, 50, .2, 100, 0]
ModEnv = [0, 0, 0.1, 1, 50, .2, 100, 0]
name = "bell.wav"

# # FM Coefficients - wood drum
# FMFreqs     = [200, 300, 400, 200] # frequency of carrier oscillator
# FMFreqRatio = [1.4, 1.4, 1.4, 0.6875] # ratio of modulator to carrier
# CarEnv = [0, .8, 20, 1, 50, .2, 100, 0]
# ModEnv = [0, 0, 0.1, 1, 12,  0, 100, 0]
# name = "wood_drum.wav"

# # FM Coefficients - chime
# FMFreqs     = [1000] # frequency of carrier oscillator
# FMFreqRatio = [2.005] # ratio of modulator to carrier
# CarEnv = [0, 0, 0.1, 1, 50, 0.2, 100, 0]
# ModEnv = [0, 0, 0.1, 1, 25, 0.2, 100, 0]
# name = "chime.wav"

# # FM Coefficients - marimba
# FMFreqs     = [400, 610, 800] # frequency of carrier oscillator
# FMFreqRatio = [2.4, 2.4, 2.4] # ratio of modulator to carrier
# CarEnv = [0, 0.8,  10, 1, 50, 0.2, 100, 0]
# ModEnv = [0,   0, 0.1, 1, 50, 0.2, 100, 0]
# name = "marimba.wav"

# Function to generate a waveform for a single note
def generate_tone(freq, duration, sample_rate):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    # Fundamental frequency
    waveform = np.sin(2 * np.pi * freq * t)
    # Add harmonics
    harmonics = [0.5, 0.3, 0.2, 0.1]
    for i, amp in enumerate(harmonics, start=2):
        waveform += amp * np.sin(2 * np.pi * freq * i * t)
    return waveform

# Function to generate a waveform for a single note
def envelopegen(envCoeff, duration, sample_rate):
    # x coordinates go from 0-100: percent of the total time duration 
    # y coords go from 0-1: amplitude scaling
    if len(envCoeff) != 8:
        raise Exception("wrong input type")

    x0, y0, x1, y1, x2, y2, x3, y3 = envCoeff
    
    attack  = np.linspace( 0, y0, int(sample_rate * (x0-0 ) * 0.01 * duration))  # Attack phase (0.1 seconds)
    decay   = np.linspace(y0, y1, int(sample_rate * (x1-x0) * 0.01 * duration )) # Decay phase (0.2 seconds)
    sustain = np.linspace(y1, y2, int(sample_rate * (x2-x1) * 0.01 * duration )) # Sustain phase (29.5 seconds)
    release = np.linspace(y2, y3, int(sample_rate * (x3-x2) * 0.01 * duration )) # Release phase (0.2 seconds)
    envelope = np.concatenate((attack, decay, sustain, release))
    
    # envelope = np.pad(envelope, (0, len(drum_sound) - len(envelope)), 'constant')
    envelope = np.pad(envelope, (0, int(duration*SAMPLE_RATE) - len(envelope)), 'constant')
    return envelope

# Generate waveforms for all freqs 
waveforms = []
for ix in range(len(FMFreqs)):
    env1 = envelopegen(CarEnv , DURATION, SAMPLE_RATE)
    env2 = envelopegen(ModEnv , DURATION, SAMPLE_RATE)
    car_waveform = generate_tone(FMFreqs[ix], DURATION, SAMPLE_RATE)
    mod_waveform = generate_tone(FMFreqs[ix]*FMFreqRatio[ix], DURATION, SAMPLE_RATE)
    wfm = env1*car_waveform + env2*mod_waveform
    waveforms.append(wfm)    

# Sum the waveforms
drum_sound = sum(waveforms)
# makeplots(t, drum_sound, SAMPLE_RATE, "Init Signal")

# Normalize to prevent clipping1
drum_sound = drum_sound / np.max(np.abs(drum_sound))

# Save to a WAV file
write(name, SAMPLE_RATE, (drum_sound * 32767).astype(np.int16))


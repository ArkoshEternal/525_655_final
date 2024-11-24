import numpy as np
from scipy.io.wavfile import write
from helper import makeplots

# Constants
SAMPLE_RATE = 44100  # Standard sample rate (44.1 kHz)
DURATION = 1.0      # Total duration of the chord (seconds)

# Coefficients
AmpEnv   = [0.1, 1, 2, 1, 50, 1, 100, 1]
FreqEnv   = [[0, 105, 33, 100, 66, 95, 100, 90]]
name = "shit.wav"

# Function to generate a waveform for a single note
def generate_fm(freqEnvCoeff, duration, sample_rate):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    freqEnv = envelopegen(freqEnvCoeff, duration, sample_rate)
    
    # Fundamental frequency
    waveform = np.sin(2 * np.pi * freqEnv * t)
    freq = freqEnv[0]
    
    # Harmonics
    harmonics = [0.5, 0.3, 0.2, 0.1]
    for i, amp in enumerate(harmonics, start=2):
        waveform += amp * np.sin(2 * np.pi * freq * i * t)

    return t, waveform

# Function to generate a waveform for a single note
def envelopegen(envCoeff, duration, sample_rate):
    # x coordinates go from 0-100: percent of the total time duration 
    # y coords go from 0-1: scaling
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
for ix in range(len(FreqEnv)):
    t, tone_waveform = generate_fm(FreqEnv[ix], DURATION, SAMPLE_RATE)
    waveforms.append(tone_waveform) 

# Sum the waveforms
drum_sound = sum(waveforms)
makeplots(t, drum_sound, SAMPLE_RATE, "Init Signal")

# Ensure the envelope matches the waveform length
envelope = envelopegen(AmpEnv , DURATION, SAMPLE_RATE)
envelope = np.pad(envelope, (0, len(drum_sound) - len(envelope)), 'constant')
makeplots(t, envelope, SAMPLE_RATE, "envelope")


# Apply the envelope to the waveform
drum_sound = drum_sound * envelope

# Normalize to prevent clipping1
drum_sound = drum_sound / np.max(np.abs(drum_sound))

# Save to a WAV file
write(name, SAMPLE_RATE, (drum_sound * 32767).astype(np.int16))


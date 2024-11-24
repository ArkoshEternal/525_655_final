import numpy as np
from scipy.io.wavfile import write
from helper import makeplots

# Constants
SAMPLE_RATE = 44100  # Standard sample rate (44.1 kHz)
DURATION = 5.0      # Total duration of the chord (seconds)

# KS Coefficients - snare1
KSLens = [800, 1000]
KSBlends = [0.5, 0.6]
name = "snare.wav"
decay = -3;

# KS Coefficients - snare2
KSLens = [4000, 2000]
KSBlends = [0.5, 0.5]
name = "snare2.wav"
decay = -1

# Karplus-Strong Algorithm
def karplus_strong(p, duration, sample_rate, blend):
    # p = length of initial wavetable
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    num_samples = int(sample_rate * duration)
    noise = np.random.uniform(-1, 1, p)
    zeros = np.zeros(num_samples-p)
    output = np.concatenate((noise,zeros))
    for ix in range(num_samples-p):
        x =  0.5 * output[ix]  + ((blend < np.random.uniform(0, 1, 1)) - 0.5) * output[ix+1]
        outix = ix+p;
        output[outix] = x[0]
        
    return t, output

# Generate waveforms for all freqs 
waveforms = []
for ix in range(len(KSLens)):
    t, note_waveform = karplus_strong(KSLens[ix], DURATION, SAMPLE_RATE, KSBlends[ix])
    waveforms.append(note_waveform)    

# Sum the waveforms
drum_sound = sum(waveforms)
makeplots(t, drum_sound, SAMPLE_RATE, "Init Signal")

# Normalize to prevent clipping1
drum_sound = drum_sound / np.max(np.abs(drum_sound))

# Apply an attach and release envelope for 5 seconds
a_dur = 0.1
r_dur = DURATION-a_dur
attack = np.linspace(0, 1, int(SAMPLE_RATE * a_dur)) # Attack phase - linear
rt = np.linspace(0, r_dur, int(SAMPLE_RATE * r_dur)) # Release phase - exp
release = np.exp(decay*rt)
envelope = np.concatenate((attack,release))

# Ensure the envelope matches the waveform length
envelope = np.pad(envelope, (0, len(drum_sound) - len(envelope)), 'constant')

# Apply the envelope to the waveform
output = drum_sound * envelope
makeplots(t, output, SAMPLE_RATE, "Out")

# Save to a WAV file
write(name, SAMPLE_RATE, (output * 32767).astype(np.int16))


import numpy as np
import matplotlib.pyplot as plt
from scipy.io.wavfile import write

# Constants
SAMPLE_RATE = 44100  # Standard sample rate for audio (44.1 kHz)
DURATION = 2.0       # Duration of the sound in seconds
FREQ = 196         # Frequency of the low E string (Hz)

# Time axis
t = np.linspace(0, DURATION, int(SAMPLE_RATE * DURATION), endpoint=False)

# Generate the fundamental frequency
waveform = np.sin(2 * np.pi * FREQ * t)

# Add harmonics (approximates a guitar's timbre)
harmonics = [0.5, 0.3, 0.2, 0.1]  # Amplitudes of harmonics
for i, amp in enumerate(harmonics, start=2):
    waveform += amp * np.sin(2 * np.pi * FREQ * i * t)

# Apply an ADSR envelope
attack = np.linspace(0, 1, int(SAMPLE_RATE * 0.1))  # Attack phase (10% of duration)
decay = np.linspace(1, 0.8, int(SAMPLE_RATE * 0.1)) # Decay phase (10% of duration)
sustain = np.linspace(0.8, 0.8, int(SAMPLE_RATE * 0.7))  # Sustain phase (70% of duration)
release = np.linspace(0.8, 0, int(SAMPLE_RATE * 0.1))    # Release phase (10% of duration)
envelope = np.concatenate((attack, decay, sustain, release))

# Ensure the envelope matches the waveform length
envelope = np.pad(envelope, (0, len(waveform) - len(envelope)), 'constant')

# Apply the envelope to the waveform
waveform = waveform * envelope

# Normalize the waveform
waveform = waveform / np.max(np.abs(waveform))

# Save to a WAV file
write("low_e_string.wav", SAMPLE_RATE, (waveform * 32767).astype(np.int16))

# Plot the waveform
plt.plot(t[:1000], waveform[:1000])  # Plot the first 1000 samples
plt.title("Waveform of Low E String")
plt.xlabel("Time (s)")
plt.ylabel("Amplitude")
plt.show()
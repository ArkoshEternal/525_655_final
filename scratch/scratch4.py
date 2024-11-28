import numpy as np
import matplotlib.pyplot as plt
from scipy.io.wavfile import write

# Constants
SAMPLE_RATE = 44100  # Standard sample rate (44.1 kHz)
DURATION = 3.0       # Duration of the chord (3 seconds)

# Chord frequencies (E Major)
FREQS = [82.41, 123.47, 164.81, 207.65, 246.94, 329.63]  # E2, B2, E3, G#3, B3, E4

# Function to generate a waveform for a single note
def generate_note(freq, duration, sample_rate):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    # Fundamental frequency
    waveform = np.sin(2 * np.pi * freq * t)
    # Add harmonics
    harmonics = [0.5, 0.3, 0.2, 0.1]
    for i, amp in enumerate(harmonics, start=2):
        waveform += amp * np.sin(2 * np.pi * freq * i * t)
    return waveform

# Generate waveforms for all chord notes
waveforms = [generate_note(freq, DURATION, SAMPLE_RATE) for freq in FREQS]

# Sum the waveforms to create the chord
chord_waveform = sum(waveforms)

# Normalize to prevent clipping
chord_waveform = chord_waveform / np.max(np.abs(chord_waveform))

# Apply an ADSR envelope to simulate plucking
attack = np.linspace(0, 1, int(SAMPLE_RATE * 0.1))  # Attack (10% of duration)
decay = np.linspace(1, 0.8, int(SAMPLE_RATE * 0.1)) # Decay (10% of duration)
sustain = np.linspace(0.8, 0.8, int(SAMPLE_RATE * 0.7))  # Sustain (70% of duration)
release = np.linspace(0.8, 0, int(SAMPLE_RATE * 0.1))    # Release (10% of duration)
envelope = np.concatenate((attack, decay, sustain, release))

# Ensure the envelope matches the waveform length
envelope = np.pad(envelope, (0, len(chord_waveform) - len(envelope)), 'constant')

# Apply the envelope to the waveform
chord_waveform = chord_waveform * envelope

# Save to a WAV file
write("e_major_chord.wav", SAMPLE_RATE, (chord_waveform * 32767).astype(np.int16))

# Plot the waveform
t = np.linspace(0, DURATION, int(SAMPLE_RATE * DURATION), endpoint=False)
plt.plot(t[:1000], chord_waveform[:1000])  # Plot the first 1000 samples
plt.title("Waveform of E Major Chord")
plt.xlabel("Time (s)")
plt.ylabel("Amplitude")
plt.show()
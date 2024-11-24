import numpy as np
import matplotlib.pyplot as plt
from scipy.io.wavfile import write

# Constants
SAMPLE_RATE = 44100  # Standard sample rate (44.1 kHz)
DURATION = 30.0      # Total duration of the chord (30 seconds)

# Chord frequencies (E Major)
FREQS = [82.41, 123.47, 164.81, 207.65, 246.94, 329.63]  # E2, B2, E3, G#3, B3, E4
DELAY_BETWEEN_STRINGS = 0.05  # Delay between strings in seconds

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

# Generate waveforms for all chord notes with delay
waveforms = []
for i, freq in enumerate(FREQS):
    note_waveform = generate_note(freq, DURATION, SAMPLE_RATE)
    # Add delay (offset) to the start of each waveform
    delay_samples = int(SAMPLE_RATE * i * DELAY_BETWEEN_STRINGS)
    delayed_waveform = np.pad(note_waveform, (delay_samples, 0), 'constant')[:len(note_waveform)]
    waveforms.append(delayed_waveform)

# Sum the waveforms to create the strummed chord
strummed_chord = sum(waveforms)

# Normalize to prevent clipping
strummed_chord = strummed_chord / np.max(np.abs(strummed_chord))

# Apply an ADSR envelope for 30 seconds
attack = np.linspace(0, 1, int(SAMPLE_RATE * 0.1))  # Attack phase (0.1 seconds)
decay = np.linspace(1, 0.9, int(SAMPLE_RATE * 0.2))  # Decay phase (0.2 seconds)
sustain = np.linspace(0.9, 0, int(SAMPLE_RATE * 29.5))  # Sustain phase (29.5 seconds)
release = np.linspace(0.9, 0, int(SAMPLE_RATE * 0.2))     # Release phase (0.2 seconds)
envelope = np.concatenate((attack, decay, sustain, release))

# Ensure the envelope matches the waveform length
envelope = np.pad(envelope, (0, len(strummed_chord) - len(envelope)), 'constant')

# Apply the envelope to the waveform
strummed_chord = strummed_chord * envelope

# Save to a WAV file
write("sustained_30s_strummed_e_major_chord.wav", SAMPLE_RATE, (strummed_chord * 32767).astype(np.int16))


import numpy as np
import matplotlib.pyplot as plt
from scipy.io.wavfile import write

# Constants
SAMPLE_RATE = 44100
TOTAL_DURATION = 20.0
CHORD_DURATION = 5.0
STRUM_DELAY = 0.03
REVERB_DECAY = 0.5
DAMPING_BASE = 0.8

# Frequencies for chords (E Major, A Major, D Major, G Major)
CHORD_FREQS = [
    [82.41, 123.47, 164.81, 207.65, 246.94, 329.63],
    [110.00, 146.83, 220.00, 246.94, 329.63, 440.00],
    [73.42, 110.00, 146.83, 220.00, 293.66, 440.00],
    [98.00, 123.47, 196.00, 246.94, 293.66, 392.00],
]

CHORD_START_TIMES = [0, 5, 10, 15]

# Function to generate a waveform for a single note with a plucked effect
def generate_note(freq, duration, sample_rate, pluck_decay=0.005):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    waveform = np.sin(2 * np.pi * freq * t)
    # Add harmonics with faster decay
    harmonics = [0.5, 0.3, 0.2, 0.1]
    for i, amp in enumerate(harmonics, start=2):
        waveform += amp * np.sin(2 * np.pi * freq * i * t) * np.exp(-pluck_decay * i * t)
    # Apply a quick pluck envelope
    pluck_envelope = np.exp(-pluck_decay * t)
    return waveform * pluck_envelope

# Function to simulate a resonating guitar body
def guitar_body_resonance(waveform, sample_rate):
    body_filter = np.array([0.6, 0.4, 0.3, 0.2])  # Example resonant frequencies
    delays = [int(sample_rate / freq) for freq in [110, 220, 330, 440]]
    body_waveform = np.zeros_like(waveform)
    for delay, strength in zip(delays, body_filter):
        delayed = np.pad(waveform, (delay, 0), mode='constant')[:-delay]
        body_waveform += strength * delayed
    return waveform + body_waveform

# Function to add fret noise
def add_fret_noise(waveform, sample_rate, noise_intensity=0.02):
    noise = np.random.uniform(-1, 1, int(sample_rate * 0.1))  # 100ms of noise
    noise *= noise_intensity
    start = int(sample_rate * 0.02)  # 20ms of delay before fret noise
    waveform[start:start + len(noise)] += noise
    return waveform

# Function to generate a strummed chord
def generate_chord(freqs, duration, sample_rate, strum_delay):
    chord_waveform = np.zeros(int(sample_rate * duration))
    for i, freq in enumerate(freqs):
        note_waveform = generate_note(freq, duration, sample_rate)
        note_waveform = guitar_body_resonance(note_waveform, sample_rate)  # Apply body resonance
        delay_samples = int(i * strum_delay * sample_rate)  # Strum delay
        padded_waveform = np.pad(note_waveform, (delay_samples, 0), 'constant')[:len(chord_waveform)]
        chord_waveform += padded_waveform
    return chord_waveform / len(freqs)

# Function to add reverb
def add_reverb(waveform, sample_rate, decay):
    reverb_waveform = np.zeros_like(waveform)
    delay_samples = int(sample_rate * 0.1)  # 100ms delay for reverb
    for i in range(1, 5):  # Add multiple reflections
        attenuated = waveform * (decay ** i)
        delayed = np.pad(attenuated, (i * delay_samples, 0), 'constant')[:len(waveform)]
        reverb_waveform += delayed
    return waveform + reverb_waveform

# Initialize the output waveform
output_waveform = np.zeros(int(SAMPLE_RATE * TOTAL_DURATION))

# Process each chord
for i, start_time in enumerate(CHORD_START_TIMES):
    # Generate the current chord
    chord_waveform = generate_chord(CHORD_FREQS[i], CHORD_DURATION, SAMPLE_RATE, STRUM_DELAY)
    # Add fret noise to the start of the chord
    chord_waveform = add_fret_noise(chord_waveform, SAMPLE_RATE)
    # Add the chord to the output waveform at the start time
    start_sample = int(start_time * SAMPLE_RATE)
    output_waveform[start_sample:start_sample + len(chord_waveform)] += chord_waveform
    # Apply dynamic dampening to all previous waveforms
    damping_factor = DAMPING_BASE ** (i + 1)
    output_waveform *= damping_factor

# Add reverb
output_waveform = add_reverb(output_waveform, SAMPLE_RATE, REVERB_DECAY)

# Normalize the final waveform
output_waveform = output_waveform / np.max(np.abs(output_waveform))

# Save to a WAV file
write("realistic_guitar_simulation.wav", SAMPLE_RATE, (output_waveform * 32767).astype(np.int16))

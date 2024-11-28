import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import convolve
from scipy.io.wavfile import write

# Constants
SAMPLE_RATE = 44100  # 44.1 kHz sample rate
CHORD_DURATION = 5.0  # Duration of each chord
TOTAL_DURATION = 20.0  # Total duration of the piece
STRUM_DELAY = 0.03  # Delay between strings (30ms)
DAMPING = 0.995  # Damping factor for string decay

# Frequencies for chords (E Major, A Major, D Major, G Major)
CHORD_FREQS = [
    [82.41, 123.47, 164.81, 207.65, 246.94, 329.63],  # E Major
    [110.00, 146.83, 220.00, 246.94, 329.63, 440.00], # A Major
    [73.42, 110.00, 146.83, 220.00, 293.66, 440.00],  # D Major
    [98.00, 123.47, 196.00, 246.94, 293.66, 392.00],  # G Major
    [110.00, 138.59, 164.81, 220.00, 277.18, 329.63],  
    [110.00, 130.81, 164.81, 220.00, 261.63, 329.63],
    [110.00, 130.81, 164.81, 220.00, 261.63, 311.13],
    [110.00, 138.59, 164.81, 220.00, 261.63, 311.13],
    [123.47, 138.59, 196.00, 246.94, 293.66, 349.23],
    [130.81, 196.00, 261.63, 329.63, 392.00, 523.25],
    [130.81, 196.00, 261.63, 329.63, 392.00, 466.16],
    [130.81, 196.00, 261.63, 329.63, 392.00, 440.00],
    [146.83, 185.00, 220.00, 293.66, 349.23, 392.00],
    [146.83, 174.61, 220.00, 293.66, 349.23, 440.00],
    [146.83, 174.61, 220.00, 293.66, 349.23, 392.00],
    [82.41, 130.81, 164.81, 196.00, 246.94, 329.63],
    [82.41, 123.47, 164.81, 196.00, 246.94, 329.63],
    [87.31, 130.81, 174.61, 261.63, 349.23, 440.00],
    [87.31, 130.81, 174.61, 261.63, 349.23, 391.99],
    [98.00, 123.47, 196.00, 246.94, 293.66, 392.00]
]

CHORD_START_TIMES = [0, 5, 10, 15]  # Chords start every 5 seconds

# Karplus-Strong Algorithm for a single string
def karplus_strong(freq, duration, sample_rate, damping):
    num_samples = int(sample_rate * duration)
    N = int(sample_rate / freq)  # Size of the delay buffer
    buffer = np.random.uniform(-1, 1, N)  # Initialize with noise
    output = np.zeros(num_samples)
    for i in range(num_samples):
        output[i] = buffer[0]
        avg = damping * 0.5 * (buffer[0] + buffer[1])
        buffer = np.append(buffer[1:], avg)
    return output

# Function to generate a chord using Karplus-Strong
def generate_chord(freqs, duration, sample_rate, strum_delay, damping):
    chord_waveform = np.zeros(int(sample_rate * duration))
    for i, freq in enumerate(freqs):
        string_waveform = karplus_strong(freq, duration, sample_rate, damping)
        delay_samples = int(i * strum_delay * sample_rate)
        padded_waveform = np.pad(string_waveform, (delay_samples, 0), 'constant')[:len(chord_waveform)]
        chord_waveform += padded_waveform
    return chord_waveform / len(freqs)

# Impulse Response for Guitar Body
def apply_impulse_response(waveform, ir_file="guitar_body_ir.wav"):
    # Load or simulate a guitar body impulse response
    ir_duration = 0.2  # Short impulse response (200ms)
    t = np.linspace(0, ir_duration, int(SAMPLE_RATE * ir_duration), endpoint=False)
    ir = np.exp(-t * 20) * np.sin(2 * np.pi * 120 * t)  # Simulated impulse response
    convolved_waveform = convolve(waveform, ir, mode='full')[:len(waveform)]
    return convolved_waveform / np.max(np.abs(convolved_waveform))

# Initialize output waveform
output_waveform = np.zeros(int(SAMPLE_RATE * TOTAL_DURATION))

# Generate the chord sequence
for i, start_time in enumerate(CHORD_START_TIMES):
    chord_waveform = generate_chord(CHORD_FREQS[i], CHORD_DURATION, SAMPLE_RATE, STRUM_DELAY, DAMPING)
    start_sample = int(start_time * SAMPLE_RATE)
    output_waveform[start_sample:start_sample + len(chord_waveform)] += chord_waveform

# Apply impulse response to mimic guitar body resonance
output_waveform = apply_impulse_response(output_waveform)

# Normalize waveform
output_waveform = output_waveform / np.max(np.abs(output_waveform))

# Save to WAV file
write("karplus_strong_guitar_simulation.wav", SAMPLE_RATE, (output_waveform * 32767).astype(np.int16))
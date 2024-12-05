import numpy as np
from scipy.signal import convolve
# file which implements the generation of guitar chords for open_synth

# Constants 
SAMPLE_RATE = 44100  # 44.1 kHz sample rate
CHORD_DURATION = 30.0  # Duration of each chord
STRUM_DELAY = 0.03  # Delay between strings (30ms)
DAMPING = 0.995  # Damping factor for string decay

# Mimic Guitar Body Resonance with Impulse Response
def apply_impulse_response(waveform):
    ir_duration = 0.2  # Short impulse response (200ms)
    t = np.linspace(0, ir_duration, int(SAMPLE_RATE * ir_duration), endpoint=False)
    ir = np.exp(-t * 20) * np.sin(2 * np.pi * 120 * t)  # Simulated impulse response
    convolved_waveform = convolve(waveform, ir, mode='full')[:len(waveform)]
    return convolved_waveform / np.max(np.abs(convolved_waveform))

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

def generate_chord(frequencies, duration, sample_rate, strum_delay, damping):
    chord_waveform = np.zeros(int(sample_rate * duration))
    for i, freq in enumerate(frequencies):
        string_waveform = karplus_strong(freq, duration, sample_rate, damping)
        delay_samples = int(i * strum_delay * sample_rate)
        padded_waveform = np.pad(string_waveform, (delay_samples, 0), 'constant')[:len(chord_waveform)]
        chord_waveform += padded_waveform
    chord_waveform = apply_impulse_response(chord_waveform)
    return chord_waveform / len(frequencies)

# Function which returns a strummed guitar chord for a given set of frequencies 
def generate_guitar_dict(mydict):
    return_dict = {}
    # Generate the chords and return them as key value pairs 
    for key, value in mydict.items(): 
        return_dict[key] = generate_chord(value, CHORD_DURATION, SAMPLE_RATE, STRUM_DELAY, DAMPING)
    return return_dict
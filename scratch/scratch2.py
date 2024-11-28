import numpy as np
from scipy.io.wavfile import write
import os

# Define guitar string frequencies (Hz) for standard tuning
guitar_frequencies = [82.41, 110.00, 146.83, 196.00, 246.94, 329.63]

# Sampling rate and duration
SAMPLE_RATE = 44100  # CD-quality audio
DURATION = 2.0  # 2 seconds per string

# Directory to save the audio files
output_directory = "./realistic_guitar_strings/"
os.makedirs(output_directory, exist_ok=True)

def generate_plucked_string(frequency, duration, sample_rate):
    """
    Generate a realistic plucked string sound using harmonics and an amplitude envelope.
    Args:
        frequency (float): Fundamental frequency of the string.
        duration (float): Duration of the sound in seconds.
        sample_rate (int): Sampling rate of the audio.
    Returns:
        np.ndarray: Synthesized audio signal.
    """
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    
    # Harmonics: Fundamental + weaker overtones
    harmonics = [1.0, 0.5, 0.3, 0.2, 0.1, 0.05]  # Amplitude scaling for harmonics
    signal = np.zeros_like(t)
    for i, amp in enumerate(harmonics):
        overtone = amp * np.sin(2 * np.pi * frequency * (i + 1) * t)
        signal += overtone
    
    # Apply an envelope: fast attack, exponential decay
    attack_time = 0.02  # 20 ms attack
    decay_time = duration - attack_time
    envelope = np.concatenate([
        np.linspace(0, 1, int(sample_rate * attack_time)),  # Attack
        np.exp(-5 * np.linspace(0, 1, int(sample_rate * decay_time)))  # Decay
    ])
    signal *= envelope[:len(signal)]
    
    # Normalize to prevent clipping
    signal = signal / np.max(np.abs(signal))
    
    return signal

# Generate and save each string's sound
for i, freq in enumerate(guitar_frequencies):
    string_sound = generate_plucked_string(freq, DURATION, SAMPLE_RATE)
    file_name = f"string_{i+1}_tone.wav"
    write(os.path.join(output_directory, file_name), SAMPLE_RATE, (string_sound * 32767).astype(np.int16))
    print(f"Generated: {file_name}")

# Combine all strings into a single file
combined_sound = np.concatenate([generate_plucked_string(f, DURATION, SAMPLE_RATE) for f in guitar_frequencies])
combined_sound = combined_sound / np.max(np.abs(combined_sound))  # Normalize
write(os.path.join(output_directory, "guitar_strings_combined.wav"), SAMPLE_RATE, (combined_sound * 32767).astype(np.int16))
print("Generated: guitar_strings_combined.wav")
import numpy as np
from scipy.io.wavfile import write

# General settings
sample_rate = 44100  # Samples per second

def sine_wave(frequency, duration, amplitude=1.0):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    return amplitude * np.sin(2 * np.pi * frequency * t)

def white_noise(duration, amplitude=1.0):
    return amplitude * np.random.uniform(-1, 1, int(sample_rate * duration))

def apply_envelope(signal, attack, decay, sustain, release):
    length = len(signal)
    envelope = np.ones(length)
    attack_samples = int(attack * sample_rate)
    decay_samples = int(decay * sample_rate)
    sustain_samples = length - attack_samples - decay_samples - int(release * sample_rate)

    # Attack
    envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
    # Decay
    envelope[attack_samples:attack_samples + decay_samples] = np.linspace(1, sustain, decay_samples)
    # Sustain
    envelope[attack_samples + decay_samples:-int(release * sample_rate)] = sustain
    # Release
    envelope[-int(release * sample_rate):] = np.linspace(sustain, 0, int(release * sample_rate))

    return signal * envelope

def kick_drum():
    # Low sine wave with decay
    kick = sine_wave(60, 0.5)  # Frequency in Hz, duration in seconds
    kick = apply_envelope(kick, 0.01, 0.2, 0.3, 0.1)
    return kick

def snare_drum():
    # White noise with a band-pass filter
    noise = white_noise(0.5)
    snare = apply_envelope(noise, 0.01, 0.1, 0.2, 0.1)
    return snare

def hi_hat():
    # High-frequency noise with a short decay
    noise = white_noise(0.2)
    hi_hat = apply_envelope(noise, 0.005, 0.05, 0.1, 0.05)
    return hi_hat * np.exp(-np.linspace(0, 1, len(noise)) * 10)  # Metallic decay

# Save to WAV function
def save_to_wav(filename, sound):
    # Normalize to 16-bit PCM format
    normalized_sound = np.int16(sound / np.max(np.abs(sound)) * 32767)
    write(filename, sample_rate, normalized_sound)

# Main Program
if __name__ == "__main__":
    print("Generating Kick Drum...")
    kick = kick_drum()
    save_to_wav("kick_drum.wav", kick)
    print("Saved kick_drum.wav")

    print("Generating Snare Drum...")
    snare = snare_drum()
    save_to_wav("snare_drum.wav", snare)
    print("Saved snare_drum.wav")

    print("Generating Hi-Hat...")
    hi_hat_sound = hi_hat()
    save_to_wav("hi_hat.wav", hi_hat_sound)
    print("Saved hi_hat.wav")

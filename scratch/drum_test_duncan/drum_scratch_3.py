import numpy as np
from scipy.io.wavfile import write

# General settings
sample_rate = 44100  # Samples per second
beat_duration = 0.5  # Duration of one beat in seconds

def sine_wave(frequency, duration, amplitude=1.0):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    return amplitude * np.sin(2 * np.pi * frequency * t)

def white_noise(duration, amplitude=1.0):
    return amplitude * np.random.uniform(-1, 1, int(sample_rate * duration))

def metallic_noise(duration, frequency=8000, amplitude=1.0):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    noise = white_noise(duration, amplitude)
    metallic = noise * np.sin(2 * np.pi * frequency * t)
    return metallic

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
    # Low sine wave for the body
    kick_body = sine_wave(60, 0.5, amplitude=1.0)
    # Noise burst for attack
    kick_attack = white_noise(0.5, amplitude=0.5)
    kick = kick_body + kick_attack
    kick = apply_envelope(kick, 0.01, 0.3, 0.2, 0.1)
    return kick

def snare_drum():
    # White noise for the snare
    snare_noise = white_noise(0.5, amplitude=0.8)
    # Resonance to mimic the drum head
    snare_body = sine_wave(200, 0.5, amplitude=0.2) + sine_wave(300, 0.5, amplitude=0.1)
    snare = snare_noise + snare_body
    snare = apply_envelope(snare, 0.01, 0.2, 0.2, 0.1)
    return snare

# def hi_hat():
#     # Metallic noise for the hi-hat
#     hi_hat_noise = metallic_noise(0.2, frequency=10000, amplitude=0.6)
#     hi_hat = apply_envelope(hi_hat_noise, 0.005, 0.05, 0.1, 0.05)
#     return hi_hat

def hi_hat():
    noise = white_noise(0.2)  # High-frequency white noise
    hi_hat = apply_envelope(noise, 0.005, 0.05, 0.1, 0.05)
    return hi_hat * np.exp(-np.linspace(0, 1, len(noise)) * 10)

def create_pattern():
    # Beat pattern
    kick = kick_drum()
    snare = snare_drum()
    hi_hat_sound = hi_hat()
    
    # Calculate length of one beat in samples
    beat_length = int(sample_rate * beat_duration)
    
    # Prepare the drum pattern (4/4)
    pattern = np.zeros(beat_length * 4)  # 4 beats per bar
    
    # Place sounds on the timeline
    for i in range(4):  # Iterate over the 4 beats
        if i % 2 == 0:  # Kick on beats 1 and 3
            pattern[i * beat_length: i * beat_length + len(kick)] += kick
        if i % 2 == 1:  # Snare on beats 2 and 4
            pattern[i * beat_length: i * beat_length + len(snare)] += snare
        
        # Hi-hat on all beats (every 8th note)
        for j in range(2):  # 8th notes per beat
            start = i * beat_length + j * (beat_length // 2)
            pattern[start: start + len(hi_hat_sound)] += hi_hat_sound

    # Normalize the pattern
    pattern = pattern / np.max(np.abs(pattern))
    return pattern

def save_to_wav(filename, sound):
    # Normalize to 16-bit PCM format
    normalized_sound = np.int16(sound / np.max(np.abs(sound)) * 32767)
    write(filename, sample_rate, normalized_sound)

# Main Program
if __name__ == "__main__":
    print("Generating 4/4 Drum Pattern...")
    drum_pattern = create_pattern()
    save_to_wav("synthetic_drum_pattern.wav", drum_pattern)
    print("Saved drum pattern to synthetic_drum_pattern.wav")

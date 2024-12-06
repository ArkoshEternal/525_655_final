import numpy as np
from scipy.io.wavfile import write
import sounddevice as sd

def generate_drum_sound(drum_name, duration=1.0, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)

    match drum_name:
        case "snare":
            # Snare drum: Combination of noise burst + sine wave for body with a sharper attack
            noise = np.random.normal(0, 1, t.shape)
            snare_wave = np.sin(2 * np.pi * 200 * t) * np.exp(-5 * t)  # Body of snare
            noise_wave = noise * np.exp(-5 * t)  # High-frequency noise for snare 'pop'
            waveform = (noise_wave + snare_wave) * 0.6  # Balance both sounds for realism
        case "hihat":
            # Hi-hat: High-frequency noise burst with some slight pitch modulation
            noise = np.random.normal(0, 1, t.shape)
            waveform = noise * np.exp(-50 * t)  # High-frequency noise, fast decay
        case "tom1": 
            # Tom 1 (low): Low frequency sine wave, slightly modulated for natural sound
            waveform = np.sin(2 * np.pi * 60 * t) * np.exp(-6 * t)
        case "tom2":
            # Tom 2 (mid): Higher tom sound with slight pitch modulation
            waveform = np.sin(2 * np.pi * 80 * t) * np.exp(-5 * t)
        case "kick":
            # Kick drum: Low sine wave with attack noise burst for punch
            low_freq = np.sin(2 * np.pi * 40 * t) * np.exp(-4 * t)  # Low punch
            noise = np.random.normal(0, 0.6, t.shape)  # Add noise for attack
            waveform = low_freq + noise * np.exp(-3 * t)  # Combine sine and noise burst
        case "crash":
            # Crash cymbal: More complex noise burst with longer decay for shimmer
            noise = np.random.normal(0, 1, t.shape)
            waveform = noise * np.exp(-2 * t)  # Less sharp decay than ride
        case "ride": 
            # Ride cymbal: High-frequency noise with smoother decay and slight frequency modulation
            noise = np.random.normal(0, 1, t.shape)
            modulated_noise = noise * np.exp(-5 * t)  # Decay with smoother tail
            # Slight pitch modulation for shimmer
            pitch_modulation = np.sin(2 * np.pi * 0.2 * t) * modulated_noise
            waveform = modulated_noise + pitch_modulation * 0.2  # Add subtle shimmer
        case "floor_tom":
            # Floor Tom: Low-frequency sine wave, longer decay for a fuller sound
            waveform = np.sin(2 * np.pi * 50 * t) * np.exp(-7 * t)
        case _:
            waveform = np.zeros_like(t)

    # Normalize the waveform to avoid clipping
    waveform = waveform / np.max(np.abs(waveform))
    return waveform

def create_fast_rock_pattern(sample_rate=44100):
    # Define the rhythm pattern for a fast ride cymbal-driven rock drumline
    pattern = [
        ("kick", 0.25), ("ride", 0.25), ("snare", 0.25), ("ride", 0.25),
        ("kick", 0.25), ("ride", 0.25), ("snare", 0.25), ("ride", 0.25),
        ("kick", 0.25), ("ride", 0.25), ("snare", 0.25), ("ride", 0.25),
        ("kick", 0.25), ("ride", 0.25), ("snare", 0.25), ("ride", 0.25)
    ]
    
    drumline = np.array([], dtype=np.float32)

    for drum, duration in pattern:
        drum_sound = generate_drum_sound(drum, duration, sample_rate)
        drumline = np.append(drumline, drum_sound)

    drumline = drumline / np.max(np.abs(drumline))
    return drumline

def play_fast_rock_drums():
    sample_rate = 44100
    drumline = create_fast_rock_pattern(sample_rate)

    print("Playing fast rock drum pattern...")
    sd.play(drumline, sample_rate)
    sd.wait()

    write("fast_rock_pattern_realistic_with_ride.wav", sample_rate, np.int16(drumline * 32767))
    print("Saved 'fast_rock_pattern_realistic_with_ride.wav'.")

# Play the fast rock drum pattern
play_fast_rock_drums()


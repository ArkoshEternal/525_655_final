import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write

def generate_drum_sound(drum_type, duration, sample_rate=44100):
    """Generate a drum sound with the given type and duration."""
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    
    if drum_type == "kick":
        waveform = np.sin(2 * np.pi * 60 * t) * np.exp(-5 * t)
    elif drum_type == "snare":
        noise = np.random.normal(0, 1, t.shape)
        waveform = noise * np.exp(-5 * t)
    elif drum_type == "hihat":
        noise = np.random.normal(0, 1, t.shape)
        waveform = noise * np.exp(-50 * t)
    elif drum_type == "crash":
        noise = np.random.normal(0, 1, t.shape)
        waveform = noise * np.exp(-3 * t)
    else:
        waveform = np.zeros_like(t)
    
    waveform = waveform / np.max(np.abs(waveform))  # Normalize to avoid clipping
    return waveform

def play_drum_line():
    """Play a simple rock drum beat with hi-hats, a crash cymbal, and a drum fill."""
    sample_rate = 44100
    bpm = 120
    beat_duration = 60 / bpm

    # Define the drum pattern
    drum_pattern = [
        ("kick", 1 * beat_duration), ("snare", 1 * beat_duration), ("kick", 1 * beat_duration), ("snare", 1 * beat_duration),
        ("kick", 0.5 * beat_duration), ("kick", 0.5 * beat_duration), ("snare", 1 * beat_duration), ("kick", 1 * beat_duration),
        ("snare", 1 * beat_duration), ("kick", 1 * beat_duration), ("snare", 1 * beat_duration), ("kick", 0.5 * beat_duration),
        ("kick", 0.5 * beat_duration), ("snare", 1 * beat_duration), ("crash", 2 * beat_duration)
    ]

    hihat_pattern = [
        ("hihat", 0.5 * beat_duration), ("hihat", 0.5 * beat_duration), ("hihat", 0.5 * beat_duration), ("hihat", 0.5 * beat_duration),
        ("hihat", 0.5 * beat_duration), ("hihat", 0.5 * beat_duration), ("hihat", 0.5 * beat_duration), ("hihat", 0.5 * beat_duration),
        ("hihat", 0.5 * beat_duration), ("hihat", 0.5 * beat_duration), ("hihat", 0.5 * beat_duration), ("hihat", 0.5 * beat_duration),
        ("hihat", 0.5 * beat_duration), ("hihat", 0.5 * beat_duration), ("hihat", 0.5 * beat_duration), ("hihat", 0.5 * beat_duration)
    ]

    # Define the drum fill
    drum_fill = [
        ("snare", 0.25 * beat_duration), ("kick", 0.25 * beat_duration), ("snare", 0.25 * beat_duration), ("kick", 0.25 * beat_duration),
        ("snare", 0.25 * beat_duration), ("kick", 0.25 * beat_duration), ("snare", 0.25 * beat_duration), ("kick", 0.25 * beat_duration)
    ]

    # Generate waveform for each drum sound
    music = np.array([], dtype=np.float32)
    for drum, duration in drum_pattern:
        music = np.append(music, generate_drum_sound(drum, duration, sample_rate))

    # Generate waveform for hi-hats
    hihat_music = np.array([], dtype=np.float32)
    for hihat, duration in hihat_pattern:
        hihat_music = np.append(hihat_music, generate_drum_sound(hihat, duration, sample_rate))

    # Generate waveform for drum fill
    fill_music = np.array([], dtype=np.float32)
    for drum, duration in drum_fill:
        fill_music = np.append(fill_music, generate_drum_sound(drum, duration, sample_rate))

    # Mix the drum sounds, hi-hats, and drum fill
    if len(hihat_music) > len(music):
        music = np.pad(music, (0, len(hihat_music) - len(music)), 'constant')
    else:
        hihat_music = np.pad(hihat_music, (0, len(music) - len(hihat_music)), 'constant')
    
    music = music + hihat_music

    # Add the drum fill at the end
    music = np.append(music, fill_music)

    # Normalize to avoid clipping
    music = music / np.max(np.abs(music))

    # Play the music
    print("Playing drum line with fill...")
    sd.play(music, sample_rate)
    sd.wait()

    # Save to file
    write("drum_line_with_fill.wav", sample_rate, np.int16(music * 32767))
    print("Saved 'drum_line_with_fill.wav'.")

# Play the drum line with fill
play_drum_line()
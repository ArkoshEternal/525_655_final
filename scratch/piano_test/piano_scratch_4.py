import numpy as np
from scipy.io.wavfile import write
import sounddevice as sd

def generate_synth_note(frequency, duration=0.5, sample_rate=44100, waveform='sine', vibrato_depth=1, vibrato_rate=4.0, velocity=0.2):
    """
    Generate a keyboard synth-like note with adjustments for a much softer sound.
    
    Args:
        frequency (float): Base frequency of the note in Hz.
        duration (float): Duration of the note in seconds.
        sample_rate (int): Sampling rate in Hz.
        waveform (str): Type of waveform ('sine', 'square', 'sawtooth', 'triangle').
        vibrato_depth (float): Depth of vibrato in Hz, lower values make vibrato subtler.
        vibrato_rate (float): Rate of vibrato in Hz, lower rates make vibrato slower.
        velocity (float): Amplitude of the note, lower values result in quieter, softer sound.
    """
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)

    # Apply vibrato (frequency modulation)
    vibrato = vibrato_depth * np.sin(2 * np.pi * vibrato_rate * t)
    modulated_frequency = frequency + vibrato

    # Generate the waveform
    if waveform == 'sine':
        note = np.sin(2 * np.pi * modulated_frequency * t)
    elif waveform == 'square':
        note = np.sign(np.sin(2 * np.pi * modulated_frequency * t))
    elif waveform == 'sawtooth':
        note = 2 * (t * modulated_frequency % 1) - 1
    elif waveform == 'triangle':
        note = 2 * np.abs(2 * (t * modulated_frequency % 1) - 1) - 1
    else:
        raise ValueError("Unsupported waveform type. Choose from 'sine', 'square', 'sawtooth', or 'triangle'.")

    # Apply a softer ADSR envelope
    attack_time = 0.1  # Slower attack for smooth onset
    decay_time = 0.1  # Slower decay for a softer drop-off
    sustain_level = 0.4  # Lower sustain level for a quieter sustain
    release_time = 0.2  # Slightly longer release time
    sustain_time = max(0, duration - (attack_time + decay_time + release_time))

    attack = np.linspace(0, 1, int(sample_rate * attack_time), endpoint=False)
    decay = np.linspace(1, sustain_level, int(sample_rate * decay_time), endpoint=False)
    sustain = np.ones(int(sample_rate * sustain_time)) * sustain_level
    release = np.linspace(sustain_level, 0, int(sample_rate * release_time), endpoint=False)

    envelope = np.concatenate((attack, decay, sustain, release))
    envelope = np.pad(envelope, (0, len(t) - len(envelope)), 'constant')
    note *= envelope

    # Apply velocity scaling (amplitude adjustment)
    note *= velocity

    # Normalize the note to avoid clipping
    note = note / np.max(np.abs(note))
    return note

def note_to_frequency(note):
    """Convert a note (e.g., A4) to its frequency."""
    note_to_semitone = {
        "C": -9, "C#": -8, "D": -7, "D#": -6, "E": -5, "F": -4, "F#": -3, "G": -2, "G#": -1,
        "A": 0, "A#": 1, "B": 2
    }
    note_name = note[:-1]
    octave = int(note[-1])
    A4_frequency = 440.0
    semitone_offset = note_to_semitone[note_name] + (octave - 4) * 12
    return A4_frequency * (2 ** (semitone_offset / 12))

def play_fur_elise_synth():
    """Play the main theme of Für Elise with a much softer synthesized sound."""
    sample_rate = 44100
    notes = [
        ("E5", 0.4), ("D#5", 0.4), ("E5", 0.4), ("D#5", 0.4), ("E5", 0.4),
        ("B4", 0.4), ("D5", 0.4), ("C5", 0.4), ("A4", 0.8),
        ("C4", 0.4), ("E4", 0.4), ("A4", 0.4), ("B4", 0.8),
        ("E4", 0.4), ("G#4", 0.4), ("B4", 0.4), ("C5", 0.8),
        ("E4", 0.4), ("E5", 0.4), ("D#5", 0.4), ("E5", 0.4), ("D#5", 0.4), ("E5", 0.4),
        ("B4", 0.4), ("D5", 0.4), ("C5", 0.4), ("A4", 0.8)
    ]

    # Generate waveform for each note
    music = np.array([], dtype=np.float32)
    for note, duration in notes:
        if note == "REST":
            music = np.append(music, np.zeros(int(sample_rate * duration)))
        else:
            freq = note_to_frequency(note)
            music = np.append(music, generate_synth_note(freq, duration, sample_rate, waveform='sine', vibrato_depth=2, vibrato_rate=4, velocity=0.2))

    # Normalize to avoid clipping
    music = music / np.max(np.abs(music))

    # Play the music
    print("Playing Für Elise (Soft Synth Version)...")
    sd.play(music, sample_rate)
    sd.wait()

    # Save to file
    write("fur_elise_soft_synth.wav", sample_rate, np.int16(music * 32767))
    print("Saved 'fur_elise_soft_synth.wav'.")

# Play Für Elise
play_fur_elise_synth()


import numpy as np
from scipy.io.wavfile import write

def generate_piano_note(note, duration=2.0, sample_rate=44100, file_name="piano_note.wav"):
    """
    Generate a piano note and save it as a .wav file.
    
    Parameters:
        note (str): Piano note in scientific notation (e.g., "A4", "C#3").
        duration (float): Duration of the note in seconds. Default is 2.0 seconds.
        sample_rate (int): Sampling rate in Hz. Default is 44100 Hz.
        file_name (str): Name of the output .wav file. Default is "piano_note.wav".
    """
    # Map of note names to semitone positions relative to A4
    note_to_semitone = {
        "C": -9, "C#": -8, "D": -7, "D#": -6, "E": -5, "F": -4, "F#": -3, "G": -2, "G#": -1,
        "A": 0, "A#": 1, "B": 2
    }
    
    # Extract the note name and octave from input
    note_name = note[:-1]
    octave = int(note[-1])
    
    # Calculate the frequency of the note
    A4_frequency = 440.0  # Hz
    semitone_offset = note_to_semitone[note_name] + (octave - 4) * 12
    frequency = A4_frequency * (2 ** (semitone_offset / 12))
    
    # Time axis
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    
    # Generate harmonics
    fundamental = np.sin(2 * np.pi * frequency * t)
    harmonic_2 = 0.5 * np.sin(2 * np.pi * 2 * frequency * t)
    harmonic_3 = 0.25 * np.sin(2 * np.pi * 3 * frequency * t)
    harmonic_4 = 0.125 * np.sin(2 * np.pi * 4 * frequency * t)
    
    # Combine harmonics
    waveform = fundamental + harmonic_2 + harmonic_3 + harmonic_4

    # Apply an ADSR envelope
    attack_time = 0.1  # seconds
    decay_time = 0.3  # seconds
    sustain_level = 0.7
    release_time = 0.4  # seconds
    sustain_time = duration - (attack_time + decay_time + release_time)
    
    attack = np.linspace(0, 1, int(sample_rate * attack_time))
    decay = np.linspace(1, sustain_level, int(sample_rate * decay_time))
    sustain = np.ones(int(sample_rate * sustain_time)) * sustain_level
    release = np.linspace(sustain_level, 0, int(sample_rate * release_time))
    
    envelope = np.concatenate((attack, decay, sustain, release))
    envelope = np.pad(envelope, (0, len(t) - len(envelope)), 'constant')
    
    # Apply the envelope
    waveform = waveform * envelope
    
    # Normalize to avoid clipping
    waveform = waveform / np.max(np.abs(waveform))
    
    # Convert to 16-bit PCM format
    waveform = np.int16(waveform * 32767)
    
    # Write to a wav file
    write(file_name, sample_rate, waveform)
    print(f"Generated piano note {note} saved as '{file_name}'")

# Example usage
generate_piano_note("C4", duration=2.0, file_name="C4_piano.wav")  # Middle C
import numpy as np
from scipy.io.wavfile import write
import sounddevice as sd
from scipy.signal import butter, lfilter

# Define constants
SAMPLE_RATE = 44100
DURATION = 2.0  # Duration of each note
NOTE_FREQUENCIES = {
    'C4': 261.63,
    'D4': 293.66,
    'E4': 329.63,
    'F4': 349.23,
    'G4': 392.00,
    'A4': 440.00,
    'B4': 466.16,
    'C5': 523.25,
    'D5': 587.33,
    'E5': 659.25,
    'F5': 698.46,
    'G5': 783.99,
    'A5': 880.00,
    
}

def analog_bd_sine(frequency, duration, sample_rate=SAMPLE_RATE):
    """Generate a basic sine wave (oscillator)."""
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    return np.sin(2 * np.pi * frequency * t)

def apply_adsr_envelope(waveform, attack, decay, sustain_level, release, sample_rate=SAMPLE_RATE):
    """Apply ADSR envelope to the waveform."""
    total_samples = len(waveform)
    
    # Calculate envelope points
    attack_samples = int(sample_rate * attack)
    decay_samples = int(sample_rate * decay)
    release_samples = int(sample_rate * release)
    
    # Calculate the maximum possible sustain samples
    sustain_samples = total_samples - attack_samples - decay_samples - release_samples
    
    # Create the ADSR envelope
    envelope = np.ones_like(waveform)  # Start with no attack
    
    # Decay: exponential drop to sustain level
    envelope[:decay_samples] = np.linspace(1, sustain_level, decay_samples)
    
    # Sustain: constant level
    envelope[decay_samples:decay_samples + sustain_samples] = sustain_level
    
    # Release: exponential drop
    envelope[-release_samples:] = np.linspace(sustain_level, 0, release_samples)
    
    # Apply envelope to waveform
    return waveform * envelope

def apply_lowpass_filter(waveform, cutoff, sample_rate=SAMPLE_RATE):
    """Apply a 12dB per octave low-pass filter."""
    nyquist = 0.5 * sample_rate
    normal_cutoff = cutoff / nyquist
    b, a = butter(4, normal_cutoff, btype='low')
    return lfilter(b, a, waveform)

def apply_lfo_finetune(waveform, lfo_freq, depth, sample_rate=SAMPLE_RATE):
    """Apply a low-frequency oscillator (LFO) to modulate fine-tuning."""
    t = np.linspace(0, len(waveform) / sample_rate, len(waveform), endpoint=False)
    lfo = np.sin(2 * np.pi * lfo_freq * t) * depth
    waveform = np.interp(t + lfo, t, waveform)  # Apply LFO modulation to waveform
    return waveform

def apply_tremolo(waveform, tremolo_freq, depth, sample_rate=SAMPLE_RATE):
    """Apply tremolo (modulation of amplitude)."""
    t = np.linspace(0, len(waveform) / sample_rate, len(waveform), endpoint=False)
    tremolo = 1 + depth * np.sin(2 * np.pi * tremolo_freq * t)  # Amplitude modulation
    return waveform * tremolo

def apply_chorus(waveform, depth=0.3, rate=0.5, sample_rate=SAMPLE_RATE):
    """Apply chorus effect (slightly delayed, detuned versions of the waveform)."""
    t = np.linspace(0, len(waveform) / sample_rate, len(waveform), endpoint=False)
    chorus_waveform = waveform.copy()
    for i in range(1, 3):  # 2 extra voices for chorus effect
        delay = int(sample_rate * (i * 0.02))  # small delay for chorus
        chorus_waveform += np.roll(waveform, delay) * (depth / i)
    
    return chorus_waveform

def generate_synth_note(frequency, duration, sample_rate=SAMPLE_RATE):
    """Generate the full synth sound for a single note."""
    
    # Step 1: Generate the fundamental sine wave
    waveform = analog_bd_sine(frequency, duration, sample_rate)
    
    # Step 2: Apply ADSR envelope (attack, decay, sustain, release)
    waveform = apply_adsr_envelope(waveform, attack=0.0, decay=2.0, sustain_level=0.1, release=0.1, sample_rate=sample_rate)
    
    # Step 3: Apply low-pass filter (12dB per octave)
    waveform = apply_lowpass_filter(waveform, cutoff=1000, sample_rate=sample_rate)
    
    # Step 4: Apply LFO to fine-tune oscillator
    waveform = apply_lfo_finetune(waveform, lfo_freq=0.1, depth=0.02, sample_rate=sample_rate)
    
    # Step 5: Apply tremolo effect
    waveform = apply_tremolo(waveform, tremolo_freq=5.0, depth=0.5, sample_rate=sample_rate)
    
    # Step 6: Apply another low-pass filter to deharshen
    waveform = apply_lowpass_filter(waveform, cutoff=2000, sample_rate=sample_rate)
    
    # Step 7: Add chorus effect
    waveform = apply_chorus(waveform, depth=0.3, rate=0.5, sample_rate=sample_rate)
    
    # Normalize waveform to avoid clipping
    waveform = waveform / np.max(np.abs(waveform))
    
    return waveform

def generate_chord(frequencies, duration, sample_rate=SAMPLE_RATE):
    """Generate a chord by combining individual notes."""
    chord_waveform = np.zeros(int(sample_rate * duration))  # Initialize the chord waveform

    for frequency in frequencies:
        note_waveform = generate_synth_note(frequency, duration, sample_rate)
        chord_waveform += note_waveform  # Add the note waveform to the chord waveform

    # Normalize the chord waveform to avoid clipping
    chord_waveform = chord_waveform / np.max(np.abs(chord_waveform))
    
    return chord_waveform

def play_song():
    """Play a short melody or song with chords."""
    # Define chord progressions
    song_chords = [
        ['C4', 'E4', 'G4'],  # C major chord
        ['D4', 'F4', 'A4'],  # D minor chord
        ['E4', 'G4', 'B4'],  # E minor chord
        ['F4', 'A4', 'C5'],  # F major chord
        ['G4', 'B4', 'D5'],  # G major chord
    ]
    
    # Concatenate all chords to form a simple progression, without dead space between them
    full_waveform = np.array([])

    for chord in song_chords:
        chord_wave = generate_chord([NOTE_FREQUENCIES[note] for note in chord], DURATION, sample_rate=SAMPLE_RATE)
        full_waveform = np.concatenate((full_waveform, chord_wave))  # Append each chord without gap

    # Play the song
    print("Playing the song...")
    sd.play(full_waveform, SAMPLE_RATE)
    sd.wait()

    # Save the waveform to a file
    write("synth_song_chords_individual_notes.wav", SAMPLE_RATE, np.int16(full_waveform * 32767))
    print("Saved 'synth_song_chords_individual_notes.wav'.")

# Play the song
play_song()

import numpy as np
from scipy.io.wavfile import write
import sounddevice as sd
from scipy.signal import butter, lfilter

# Define constants
SAMPLE_RATE = 44100
DURATION = 2.0  # Duration of the note
FREQUENCY = 440  # Frequency of the note (A4)

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
    
    # If the sustain samples would be negative, adjust the ADSR envelope duration
    if sustain_samples < 0:
        # Calculate the total length of the ADSR without sustain
        total_adsr_length = attack_samples + decay_samples + release_samples
        
        # Calculate the new decay to sustain ratio
        new_decay_samples = max(0, int((decay_samples + sustain_samples) / 2))
        
        # Adjust sustain samples to be positive, and shift decay if necessary
        sustain_samples = total_samples - attack_samples - new_decay_samples - release_samples
        decay_samples = new_decay_samples
    
    # Create the ADSR envelope
    envelope = np.zeros_like(waveform)
    
    # Attack: linear rise
    envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
    
    # Decay: exponential drop to sustain level
    envelope[attack_samples:attack_samples + decay_samples] = np.linspace(1, sustain_level, decay_samples)
    
    # Sustain: constant level
    envelope[attack_samples + decay_samples:attack_samples + decay_samples + sustain_samples] = sustain_level
    
    # Release: exponential drop
    envelope[-release_samples:] = np.linspace(sustain_level, 0, release_samples)
    
    # Apply envelope to waveform
    return waveform * envelope

def apply_lowpass_filter(waveform, cutoff, sample_rate=SAMPLE_RATE):
    """Apply a 12dB per octave low-pass filter."""
    # Normalize the cutoff frequency
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

def apply_ac_hum(waveform, hum_freq, hum_duration=0.2, sample_rate=SAMPLE_RATE):
    """Simulate AC hum oscillator at start."""
    t = np.linspace(0, hum_duration, int(sample_rate * hum_duration), endpoint=False)
    hum = 0.1 * np.sin(2 * np.pi * hum_freq * t)  # Hum signal
    hum = np.pad(hum, (0, len(waveform) - len(hum)))  # Pad hum to match the length of the waveform
    return np.concatenate([hum, waveform])

def apply_chorus(waveform, depth=0.3, rate=0.5, sample_rate=SAMPLE_RATE):
    """Apply chorus effect (slightly delayed, detuned versions of the waveform)."""
    t = np.linspace(0, len(waveform) / sample_rate, len(waveform), endpoint=False)
    chorus_waveform = waveform.copy()
    for i in range(1, 3):  # 2 extra voices for chorus effect
        delay = int(sample_rate * (i * 0.02))  # small delay for chorus
        chorus_waveform += np.roll(waveform, delay) * (depth / i)
    
    return chorus_waveform

def generate_synth_sound(frequency, duration, sample_rate=SAMPLE_RATE):
    """Generate the full synth sound based on the description."""
    
    # Step 1: Pick the fundamental sine wave
    waveform = analog_bd_sine(frequency, duration, sample_rate)
    
    # Step 2: Apply ADSR envelope (attack, decay, sustain, release)
    waveform = apply_adsr_envelope(waveform, attack=0.01, decay=2.0, sustain_level=0.1, release=0.1, sample_rate=sample_rate)
    
    # Step 3: Apply low-pass filter (12dB per octave)
    waveform = apply_lowpass_filter(waveform, cutoff=1000, sample_rate=sample_rate)
    
    # Step 4: Add 5 voices of unison with slight detuning
    voices = np.zeros_like(waveform)
    for i in range(5):
        detune = 0.2 * np.random.randn()  # Slight random detune
        voices += analog_bd_sine(frequency + detune, duration, sample_rate)
    waveform = voices / 5  # Average voices
    
    # Step 5: Apply LFO to fine-tune oscillator
    waveform = apply_lfo_finetune(waveform, lfo_freq=0.1, depth=0.02, sample_rate=sample_rate)
    
    # Step 6: Add tremolo effect
    waveform = apply_tremolo(waveform, tremolo_freq=5.0, depth=0.5, sample_rate=sample_rate)
    
    # Step 7: Add AC hum at start
    waveform = apply_ac_hum(waveform, hum_freq=60, hum_duration=0.2, sample_rate=sample_rate)
    
    # Step 8: Add another low-pass filter to deharshen
    waveform = apply_lowpass_filter(waveform, cutoff=2000, sample_rate=sample_rate)
    
    # Step 9: Add chorus effect
    waveform = apply_chorus(waveform, depth=0.3, rate=0.5, sample_rate=sample_rate)
    
    # Normalize waveform to avoid clipping
    waveform = waveform / np.max(np.abs(waveform))
    
    return waveform

def play_song(frequency, duration, sample_rate=SAMPLE_RATE):
    """Play and save the generated synth sound."""
    waveform = generate_synth_sound(frequency, duration, sample_rate)
    
    # Play the waveform using sounddevice
    print("Playing synth sound...")
    sd.play(waveform, sample_rate)
    sd.wait()
    
    # Save the waveform to a file
    write("synth_sound.wav", sample_rate, np.int16(waveform * 32767))
    print("Saved 'synth_sound.wav'.")

# Generate and play a note
play_song(440, DURATION)

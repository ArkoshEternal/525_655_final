import numpy as np
import matplotlib.pyplot as plt
from scipy.io.wavfile import write
from scipy.fft import fft, fftfreq
import math


# Constants
SAMPLE_RATE = 44100  # Standard sample rate for audio (44.1 kHz)
DURATION = 2.0       # Duration of the sound in seconds
FREQ = 82.41         # Frequency of the low E string (Hz)


# Helper Functions
def makeplots(t, waveform, SAMPLE_RATE, signame):
    plt.plot(t, waveform)  # Plot the first 1000 samples
    plt.title(signame)
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude")
    plt.show()
    
    yf = fft(waveform)
    xf = fftfreq(len(waveform), 1 / SAMPLE_RATE)  # 1 / sampling rate
    
    samps = 15000
    
    plt.plot(xf[0:samps], np.abs(yf[0:samps]))
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Amplitude')
    plt.title('FFT of the ' + signame)
    plt.show()

    
def midpoint(arr):
  n = len(arr)
  if n % 2 == 0:
    return (arr[n // 2 - 1] + arr[n // 2]) / 2
  else:
    return arr[n // 2]


# Time axis
t = np.linspace(0, DURATION, int(SAMPLE_RATE * DURATION), endpoint=False)

# Generate the fundamental frequency
waveform = np.sin(2 * np.pi * FREQ * t)

makeplots(t, waveform, SAMPLE_RATE, "Sine Wave")

# Add harmonics (approximates a guitar's timbre)
harmonics = [0.5, 0.3, 0.2, 0.1]  # Amplitudes of harmonics
for i, amp in enumerate(harmonics, start=2):
    waveform += amp * np.sin(2 * np.pi * FREQ * i * t)

makeplots(t, waveform, SAMPLE_RATE, "Harmonics")

# Apply an ADSR envelope
attack = np.linspace(0, 1, int(SAMPLE_RATE * 0.1))  # Attack phase (10% of duration)
decay = np.linspace(1, 0.8, int(SAMPLE_RATE * 0.1)) # Decay phase (10% of duration)
sustain = np.linspace(0.8, 0.8, int(SAMPLE_RATE * 0.7))  # Sustain phase (70% of duration)
release = np.linspace(0.8, 0, int(SAMPLE_RATE * 0.1))    # Release phase (10% of duration)
envelope = np.concatenate((attack, decay, sustain, release))

# Ensure the envelope matches the waveform length
envelope = np.pad(envelope, (0, len(waveform) - len(envelope)), 'constant')
makeplots(t, envelope, SAMPLE_RATE, "Envelope")

# Apply the envelope to the waveform
waveform = waveform * envelope

# Normalize the waveform
waveform = waveform / np.max(np.abs(waveform))
makeplots(t, waveform, SAMPLE_RATE, "Output")

# Save to a WAV file
write("low_e_string.wav", SAMPLE_RATE, (waveform * 32767).astype(np.int16))



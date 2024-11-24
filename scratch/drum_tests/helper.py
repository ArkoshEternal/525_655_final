import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq
import numpy as np

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
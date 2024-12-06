import numpy as np 
import sounddevice as sd
# File which generates the drum soiunds for the open_synth program

def generate_drum_sound(drum_name, duration=1.0, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)

    match drum_name:
        case "snare":
            noise = np.random.normal(0, 1, t.shape)
            waveform = noise * np.exp(-5 * t)
        case "hihat":
            noise = np.random.normal(0, 1, t.shape)
            waveform = noise * np.exp(-50 * t)
        case "tom1": 
            waveform = np.sin(2 * np.pi * 60 * t) * np.exp(-5 * t)
        case "tom2":
            waveform = np.sin(2 * np.pi * 80 * t) * np.exp(-5 * t)
        case "kick":
            low_freq = np.sin(2 * np.pi * 40 * t) * np.exp(-4 * t)  # Low punch
            noise = np.random.normal(0, 0.6, t.shape)  
            waveform = low_freq + noise * np.exp(-3 * t) # Add noise
        case "crash":
            noise = np.random.normal(0, 1, t.shape)
            waveform = noise * np.exp(-3 * t)
        case "ride": 
            noise = np.random.normal(0, 1, t.shape)
            waveform = noise * np.exp(-3 * t)
        case "floor":
            waveform = np.sin(2 * np.pi * 40 * t) * np.exp(-5 * t)
        case _:
            raise ValueError("Unsupported drum type detected in config. Please provide valid config")

         # Normalize the waveform to avoid clipping
    waveform = waveform / np.max(np.abs(waveform))
    return waveform

def generate_drum_dict(mylist): 
    return_dict = {} 
    # Generate the drum sounds and return them as key value pairs
    for key in mylist.keys():  
        return_dict[key] = generate_drum_sound(key)
    return return_dict
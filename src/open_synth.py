import json
import os
import argparse
import numpy as np
from pydub.generators import Sine
import pygame
from sshkeyboard import listen_keyboard, stop_listening
from threading import Thread
import sys
import time
import pickle
from instruments.bass import generate_bass_dict
from instruments.drum import generate_drum_dict
from instruments.guitar import generate_guitar_dict
from instruments.piano import generate_piano_dict

# Global variables
instruments = [] 
mappings = {}
sounds = {}
is_playing = False

# TODO: Create a WAV file from a script
def create_wav(script_path):
    return

# configure default key mappings
def configure_default_mappings():
    default_keys = ['a', 's', 'd', 'f', 'g', 'h']  # List of default keys
    for instrument in sounds.keys():
        mappings[instrument] = {}
        notes = list(sounds[instrument].keys())
        for i, note in enumerate(notes[:6]):  # Map only the first 6 notes
            mappings[instrument][default_keys[i]] = note

# Load configuration from JSON
def load_config(file_path):
    cache_file = "sounds_cache.pkl"

    if os.path.exists(cache_file):
        print("Cached sounds found. Loading from cache.")
        with open(cache_file, "rb") as file:
            sounds = pickle.load(file)
    else:
        print("No cached sounds found. Generating sounds from config...")
        print("This might take a while")
        # Parse JSON 
        with open(file_path, "r") as file:
            config = json.load(file)
        # Generate Sounds We'll Be Using
        for instrument in config.items():
            match instrument[0]:
                case "piano": 
                    sounds["piano"] = generate_piano_dict(config["piano"])
                    instruments.append("piano")
                case "guitar":
                    sounds["guitar"] = generate_guitar_dict(config["guitar"])
                    instruments.append("guitar")
                case "bass":
                    sounds["bass"] = generate_bass_dict(config["bass"])
                    instruments.append("bass")
                case "drum":
                    sounds["drum"] = generate_drum_dict(config["drum"])
                    instruments.append("drum")
        # Cache the sounds
        with open(cache_file, "wb") as file:
            pickle.dump(sounds, file)
        
        # Set Up Default Key Mappings
        configure_default_mappings()
        
# Play a sound using pygame
def play_sound(freq, duration=1.0, volume=0.5):
    sound = Sine(freq).to_audio_segment(duration=duration*1000, volume=volume)
    raw_data = np.frombuffer(sound.raw_data, dtype=np.int16)
    pygame.mixer.init(frequency=sound.frame_rate, size=-16, channels=1)
    pygame.mixer.Sound(buffer=raw_data.tobytes()).play()

# Map keys to playbacks
def configure_key_mapping():
    print("Press keys to map them to instrument sounds. Type 'exit' to stop. Press 'Enter' to skip.")
    for instrument, notes in sounds.items():
        print(f"\nConfiguring {instrument}:") 
        for note in notes.keys():
            print(f"Press a key for {note}: ", end="", flush=True)
            key = input().strip().lower()
            if key == "exit":
                break
            mappings[instrument][key] = note
    print("Configuration complete!")

# Keyboard listener for play mode
def play_mode():
    def on_press(key):
        try:
            key_char = key.char.lower()
            instrument = mappings["instrument"]
            if key_char in mappings[instrument]:
                note = mappings[instrument][key_char]
                if instrument == "keyboard":
                    play_sound(sounds[instrument][note])
                elif instrument in ["guitar", "bass"]:
                    for freq in sounds[instrument][note]:
                        Thread(target=play_sound, args=(freq, 0.5)).start()
                elif instrument == "drum":
                    print(f"Playing drum sound: {note}")
        except AttributeError:
            pass

    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    print("Play mode activated! Use the mapped keys to play sounds. Press 'Ctrl+C' to exit.")
    listener.join()

def main_menu():
    while True:
        choice = input(":").strip()
        if choice == "m":
            configure_key_mapping()
        elif choice == "i":
            print("Available instruments:", list(sounds.keys()))
            instrument = input("Enter instrument name: ").strip().lower()
            if instrument in sounds:
                mappings["instrument"] = instrument
                print(f"Switched to instrument: {instrument}")
            else:
                print("Invalid instrument name.")
        elif choice == "p":
            play_mode()
        elif choice == "q":
            print("See You Space Cowboy...")
            break
        elif choice == "h":
            print("m: Key mapping mode")
            print("i: Instrument select mode")
            print("p: Play mode")
            print("q: Quit")
            print("h: Help")
        else:
            print("invalid choice. press h for help")

def print_welcome(): 
    message = """
Valid Config Detected... 

Booting Up open_synth...

===========================================================================
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
===========================================================================
                                                            ,--.  ,--.     
 ,---.  ,---.  ,---. ,--,--,        ,---.,--. ,--.,--,--, ,-'  '-.|  ,---. 
| .-. || .-. || .-. :|      \      (  .-' \  '  / |      \\'-.  .-'|  .-.  |
' '-' '| '-' '\   --.|  ||  |,----..-'  `) \   '  |  ||  |  |  |  |  | |  |
 `---' |  |-'  `----'`--''--''----'`----'.-'  /   `--''--'  `--'  `--' `--'
       `--'                              `---'                             
===========================================================================
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
===========================================================================
Welcome to Open Synthesizer! Lets make some music!
"""
    lines = message.split('\n')
    for line in lines:
        for char in line:
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(0.005)  # Adjust the delay for each character
        sys.stdout.write('\n')
        sys.stdout.flush()
        time.sleep(0.5)  # Adjust the delay between lines

def wait_esc(key):
    time.sleep(0.1)

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="open_synthesizer - A deceptively simple synthesizer program")
    parser.add_argument("config", help="Path to the configuration file")
    # default to live play mode, but can also use a script to generate sounds if specified
    parser.add_argument("--script", help="Path to the script file for generating sounds")
    args = parser.parse_args()

    # Load configuration from JSON file
    load_config(args.config)
    if args.script:
        # start in script mode
        create_wav(args.script)
    # Else, load default key mappings and start the main menu
    else:
        # Set up escape as callback hotkey 
        print_welcome()
        # Wait for Escape
        listen_keyboard(on_press=wait_esc)
        main_menu()

# Launch the program 
if __name__ == "__main__": 
    main()
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
import io
# sample call: py -m open_synth test_config.json --script test_script.json
# run config arguments: test_config.json --script test_script.json

# Global variables
instruments = [] 
mappings = {}
sounds = {}
is_playing = False
cur_instrument = None

# TODO: Create a WAV file from a script
def create_wav(script_path):
    return

#    # Import JSON
#    print("Reading Script")
#    file = open(script_path, "r")
#    script = json.load(file)
#
#    # Debug Prints
#    print ("    Song SongDuration_s: " + str(script["SongDuration_s"]))
#    print ("    SongFreq_Hz: " + str(script["SongFreq_Hz"]))
#    print ("    Sounds: ")
#
#    for index, sound in enumerate(script["Sounds"]):
#        print("    Sound " + str(index))
#        print("        Instrument: " + sound["Instrument"])
#        print("        SoundName: " + sound["SoundName"])
#        print("        NoteFreq_Hz: " + str(sound["NoteFreq_Hz"]))
#        print("        Iterations: " + str(sound["Iterations"]))
#
#    # Build Timeline of Sounds    
#    
#    # Stream sounds to .wav
#
#    # Done
#    print("Loaded Script")
#    return

# Load configuration from JSON
def load_config(file_path):
    global mappings, instruments, sounds, cur_instrument
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
                # case "piano": 
                #     sounds["piano"] = generate_piano_dict(config["piano"])
                # case "guitar":
                #     sounds["guitar"] = generate_guitar_dict(config["guitar"])
                # case "bass":
                #     sounds["bass"] = generate_bass_dict(config["bass"])
                case "drum":
                    sounds["drum"] = generate_drum_dict(config["drum"])
        # Cache the sounds
        with open(cache_file, "wb") as file:
            pickle.dump(sounds, file)
    
    # Populate Instruments
    instruments = list(sounds.keys())
    cur_instrument = instruments[0]

    
    # Set up default mappings
    mappings = {instrument: {} for instrument in instruments}

# Map keys to playbacks
def configure_key_mapping():
    global mappings, instruments, sounds
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

# Callback function for playing notes
def play_note(key):
    global mappings, sounds, cur_instrument
    if key in mappings[cur_instrument]:
        note = sounds[cur_instrument][mappings[cur_instrument][key]]
        scaled_sound = np.int16(note/np.max(np.abs(note)) * 32767)
        pygame.mixer.Sound(buffer=scaled_sound.tobytes()).play()

# Keyboard listener for play mode
def play_mode():
    global is_playing, cur_instrument
    print("Entering Play Mode. You're currently playing:", cur_instrument)
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
    listen_keyboard(on_press=play_note)
    pygame.mixer.quit()
    main_menu() # return to main menu after stopping the listener

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
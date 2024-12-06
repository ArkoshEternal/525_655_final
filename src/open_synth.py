import json
import os
import argparse
import numpy as np
import pygame
import sys
import time
import pickle
from scipy.io.wavfile import write
from sshkeyboard import listen_keyboard
from instruments.bass import generate_bass_dict
from instruments.drum import generate_drum_dict
from instruments.guitar import generate_guitar_dict
from instruments.piano import generate_piano_dict
from ascii_animator import Animator, Speed, AsciiAnimation

# sample call: py -m open_synth test_config.json --script test_script.json
# run config arguments: test_config.json --script test_script.json

# Global variables
instruments = [] 
mappings = {}
sounds = {}
is_playing = False
cur_instrument = None
channels = []

def see_you_space_cowboy():
    speed = Speed.VERY_SLOW
    Animator(animation=AsciiAnimation('./random/see-you.gif'), show_axis=False, speed=speed, max_loops=1, first_cycle_sleep=False)
    print("\n\nSee You Space Cowboy")
    exit()

def create_wav(script_path):
    global sounds
    with open(script_path, "r") as file:
        script = json.load(file)
    song_duration = script["song_duration_s"]
    sample_rate = script["sample_rate"]
    song_len = int(song_duration * sample_rate)
    total_len = int(song_duration * sample_rate * 5)
    song = np.zeros(total_len)

    for sound in script["sounds"]: 
        instrument = sound["instrument"]
        sound_name = sound["sound_name"]
        start_time = sound["start_time"]

        if instrument not in sounds:
            print(f"Error: Instrument {instrument} not found in configuration")
            return
        
        if sound_name not in sounds[instrument]:
            print(f"Error: Sound {sound_name} not found in configuration")
            return
        
        sound_data = sounds[instrument][sound_name]
        sound_len = len(sound_data)
        start_idx = int(start_time * sample_rate)
        end_idx = start_idx + sound_len
        if end_idx > total_len:
            print(f"Error: Sound {sound_name} starts after the song ends")
            return
        song[start_idx:end_idx] += sound_data

    # truncate song total_len
    song = song[:song_len]
    scaled_song = np.int16(song/np.max(np.abs(song)) * 32767)
    write("output.wav", sample_rate, scaled_song)

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
                case "piano": 
                    sounds["piano"] = generate_piano_dict(config["piano"])
                case "guitar":
                    sounds["guitar"] = generate_guitar_dict(config["guitar"])
                case "bass":
                    sounds["bass"] = generate_bass_dict(config["bass"])
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
    global mappings, sounds, cur_instrument, channels
    if key in mappings[cur_instrument]:
        note = sounds[cur_instrument][mappings[cur_instrument][key]]
        scaled_sound = np.int16(note/np.max(np.abs(note)) * 32767)
        sound = pygame.mixer.Sound(buffer=scaled_sound.tobytes())
        for channel in channels:
            if not channel.get_busy():
                channel.play(sound)
                break

# Keyboard listener for play mode
def play_mode():
    global is_playing, cur_instrument, channels
    print("Entering Play Mode. You're currently playing:", cur_instrument)
    pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)
    pygame.mixer.set_num_channels(16)
    channels = [pygame.mixer.Channel(i) for i in range(pygame.mixer.get_num_channels())]
    listen_keyboard(on_press=play_note)
    pygame.mixer.quit()
    main_menu() # return to main menu after stopping the listener

def main_menu():
    global cur_instrument
    while True:
        choice = input(":").strip()
        if choice == "m":
            configure_key_mapping()
        elif choice == "i":
            print("Available instruments:", list(sounds.keys()))
            instrument = input("Enter instrument name: ").strip().lower()
            if instrument in sounds:
                cur_instrument = instrument
                print(f"Switched to instrument: {instrument}")
            else:
                print("Invalid instrument name.")
        elif choice == "p":
            play_mode()
        elif choice == "q":
            see_you_space_cowboy()
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
        time.sleep(0.1)  # Adjust the delay between lines

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
        see_you_space_cowboy()
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
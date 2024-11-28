# Top Level File Which Runs the Synth 

import json 
import pygame
from pydub import AudioSegment
from pydub.playback import play
import threading 
import argparse

# load configuration file
def load_config(file_path): 
    with open(file_path, 'r') as f: 
        return json.load(f)



def main(): 
    parser = argparse.ArgumentParser(description='open_synth program')
    
    # JSON File
    parser.add_argument('--config_file', type=str, required=True,help='Path to Config File')
    
    # Initialize pygame 
    pygame.mixer.init()

    # Synthesize from Config


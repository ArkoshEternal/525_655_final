clear
close all

sounds = struct('Instrument',"samp",...
    'SoundName' , "samp", ...     % Sound Name - check if exists
    'NoteFreq_Hz'  , 0    , ...   % Note Freq - must be divisor of Song Freq
    'Iterations', 0   ...         % Number of times to play this note/chord
    );

ix = 1;
sounds(ix).Instrument  = "piano";
sounds(ix).SoundName   = "A0";
sounds(ix).NoteFreq_Hz = 10;
sounds(ix).Iterations  = 100;
ix = ix+1;

sounds(ix).Instrument  = "piano";
sounds(ix).SoundName   = "A#0";
sounds(ix).NoteFreq_Hz = 20;
sounds(ix).Iterations  = 50;
ix = ix+1;

sounds(ix).Instrument  = "piano";
sounds(ix).SoundName   = "B0";
sounds(ix).NoteFreq_Hz = 30;
sounds(ix).Iterations  = 25;
ix = ix+1;
 

% sounds(ix).Instrument  = "guitar";
% sounds(ix).SoundName   = "GMJ";
% sounds(ix).NoteFreq_Hz = 15;
% sounds(ix).Iterations  = 100;
% ix = ix+1;
 
% sounds(ix).Instrument  = "bass";
% sounds(ix).SoundName   = "D#1";
% sounds(ix).NoteFreq_Hz = 30;
% sounds(ix).Iterations  = 100;
% ix = ix+1;
 
% sounds(ix).Instrument  = "drum";
% sounds(ix).SoundName   = "snare";
% sounds(ix).NoteFreq_Hz = 60;
% sounds(ix).Iterations  = 100;
% ix = ix+1;
 
 
top = struct('SongDuration_s', 5  ,...
    'SongFreq_Hz',60,... % Notes Per Second
    'Sounds',sounds);

x = jsonencode(top,PrettyPrint=true)

writelines(x,"test_script.json")
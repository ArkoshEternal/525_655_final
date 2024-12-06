wvname =  fullfile( fileparts(mfilename('fullpath')) , 'TestSet', sprintf('Sample%i.wav',sampleNum));

if debug

    figure();
    subplot(2,1,1)
    spectrogram(signal,frameSize)
    title('Original Signal')
    subplot(2,1,2)
    spectrogram(final,frameSize)
    title('Recreated Signal')
end
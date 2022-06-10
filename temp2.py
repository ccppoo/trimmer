from scipy.io import wavfile
from audiotsm.io.wav import WavReader, WavWriter

sampleRate, audioData = wavfile.read( "audio.wav")

# maxAudioVolume = getMaxVolume(audioData)
audioSampleCount = audioData.shape[0]

videoLength = audioData.shape[0] / sampleRate

print(f'{sampleRate=}')
print(f'{audioData.shape[0]=}')
print(f'{videoLength=}')
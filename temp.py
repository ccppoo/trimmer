import pathlib
from scipy.io import wavfile
import os
import numpy as np
import math
import matplotlib.pyplot as plt

def getMaxVolume(s):
    maxv = float(np.max(s))
    minv = float(np.min(s))
    return max(maxv,-minv)

frameRate = 30

sampleRate, audioData = wavfile.read(str(pathlib.Path(os.getcwd(), "audio.wav")))
print(audioData)
print(f"{sampleRate=}")
print(f"{ getMaxVolume(audioData)=}")
exit()
maxAudioVolume = getMaxVolume(audioData)
audioSampleCount = audioData.shape[0]

# 앞으로 전환할 필요한 한 프레임당 오디오의 샘플 레이트
# samplesPerFrame=1470.0 == 44,100 / 30
samplesPerFrame = sampleRate/frameRate

print(f"number of channels = {audioData.shape[1]}")
# 9.535986394557822 == 420537(오디오 개수?) / 44,100(Hz)
length = audioData.shape[0] / sampleRate

audioSampleCount = audioData.shape[0]

# 44,100 == audioData.shape[0] / length
# 44,100 == 420537 / 9.535986394557822
print(f"length = {length}s")
print(f"{audioData=}")
print(f"{maxAudioVolume=}") # 3368.0
print(f"{audioSampleCount=}") # 420537

# time = np.linspace(0., length, audioData.shape[0])
# plt.plot(time, audioData[:, 0], label="Left channel")
# plt.plot(time, audioData[:, 1], label="Right channel")
# plt.legend()
# plt.xlabel("Time [s]")
# plt.ylabel("Amplitude")
# plt.show()

# audioSampleCount/samplesPerFrame = 286.0795918367347
# 420537          / 1470
audioFrameCount = int(math.ceil(audioSampleCount/samplesPerFrame))

# math.ceil(audioSampleCount/samplesPerFrame) = 287
hasLoudAudio = np.zeros(audioFrameCount)

"""
hasLoudAudio는 가지고 있는 오디오 샘플(420537개)들을 프레임당 필요한 오디오 샘플(1470개)로 나눈다.
그래서 287이라는 값이 나오는데, 이것이 한 프레임당 큰 소리가 있는지 확인하는 작업이다.

우리가 만들려는 영상의 초당 프레임(30 fps)인데
즉, 영상의 총 길이 9.536(초) * 30(fps) == 287 이다.

즉, 우리가 만들 영상에는 총 (약) 287 프레임이 있는데
한 프레임당 나오는 소리 샘플들 중에서 큰 소리(큰 소리의 기준은 args에 있음)를 선별하는 작업이다.
"""
print(f'{audioSampleCount/samplesPerFrame=}')
print(f'{int(math.ceil(audioSampleCount/samplesPerFrame))=}')
print(audioFrameCount)
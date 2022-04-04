import os
import pathlib
from pytube import YouTube
import pytube
from typing import List
from utils import reflectIncrement

def download_from_Youtube(url) -> os.PathLike :
    '''
    다운로드한 영상의 제목을 가진 폴더 내부에 작업 시작

    같은 이름을 가진 영상의 경우 지금은 일단 구분 안함 (나중에 채널 이름별로 분류할지는 모름)
    '''

    # 화질 문제있음 --> 고화질로 다운 받는 방법?

    stream_list : List[pytube.Stream] = YouTube(url).streams

    for x in YouTube(url).streams:
        print(x)
    # 137 video, 251 audio
    # YouTube(url).streams.get_by_itag(137).download()
    print()
    exit()
    name = YouTube(url).streams.first().download() # returns full path
    newname = reflectIncrement(name.replace(' ','_'))
    
    os.rename(name, newname)

    return newname

def progressive_stream(url):
    YouTube(url).streams.filter(progressive=True)

def DASH_stream(url):
    # DASH stream
    YouTube(url).streams.filter(adaptive=True)

def audio_only(url):
    '''
    webm, mp4 형식으로 나옴
    
    '''
    # opus, mp4a.40.2, mp4a.40.5
    return YouTube(url).streams.filter(only_audio=True).order_by('abr').desc()

def mp4_only(url):
    # 압축 효율 AV01 > VP9 > AVC1
    '''
    av01.0.08M.08
    avc1.640028

    av01.0.05M.08
    avc1.4d401f
    '''
    # <스트림 객체>.itag 이렇게 통해서 다운로드할 수 있는 tag를 가져올 수 있음
    # Progressive stream에는 오디오랑 영상이 있음
    return YouTube(url).streams.filter(file_extension='mp4').order_by('resolution').desc()


aa = "https://www.youtube.com/watch?v=JiX7JYiMxeU&ab_channel=%EA%B0%90%EC%97%BC%EB%90%9C%EC%A0%9C%EB%9D%BC%ED%88%B4InfestedZeratul"

for x in audio_only(aa):
    print(x)

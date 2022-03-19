import os
import pathlib
from pytube import YouTube
from utils import reflectIncrement

def download_from_Youtube(url) -> os.PathLike :
    '''
    다운로드한 영상의 제목을 가진 폴더 내부에 작업 시작

    같은 이름을 가진 영상의 경우 지금은 일단 구분 안함 (나중에 채널 이름별로 분류할지는 모름)
    '''

    # 화질 문제있음 --> 고화질로 다운 받는 방법?
    name = YouTube(url).streams.first().download() # returns full path
    newname = reflectIncrement(name.replace(' ','_'))
    
    os.rename(name, newname)

    return newname
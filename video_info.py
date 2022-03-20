from utils import make_process
import os
import pathlib
import subprocess
import json

"""
원본 코드에서도 input.mp4 라고 하드 코딩되어 있는데 아마 의미는 없는 이름이고(확장자로 컴퓨터 기능 파악하려는 듯)
아래 내용을 보기 위해서 사용되는 커맨드임

일반 터미널 명령에서 2>&1 는 stderr에서 stdout으로 리다이렉트함

>> ffmpeg -i test.mkv 2>&1 # 하면 나오는 것들 ↓↓↓

Input #0, matroska,webm, from 'test.mkv':
Metadata:
    ENCODER         : Lavf58.76.100
Duration: 00:00:09.60, start: 0.000000, bitrate: 720 kb/s
Stream #0:0: Video: h264 (High), yuv420p(tv, bt709, progressive), 1920x1200 [SAR 1:1 DAR 8:5], 60 fps, 60 tbr, 1k tbn (default)
    Metadata:
    DURATION        : 00:00:09.600000000
Stream #0:1: Audio: aac (LC), 48000 Hz, stereo, fltp (default)
    Metadata:
    title           : simple_aac_recording
    DURATION        : 00:00:09.536000000

아래 명령어를 보니 프레임레이트를 알기 위한 과정으로 파악됨

근데 "input.mp4"으로 하드 코딩할게 아니라 사용자가 넣은 동영상 이름을 넣어야하는데 실수한듯?
그래서 args 기본값 frame_rate = 30.0 으로 계속 나오는거임
"""

def get_video_info(video_path : os.PathLike, workspace_path : os.PathLike):
    processtr = make_process(
        f"ffprobe -v quiet -print_format json -show_format -show_streams",
        f'{video_path}',
        ">",
        pathlib.Path(workspace_path, 'params.json')
    )

    subprocess.call(processtr, shell=True)  # Why works after I changed to True?

    with open(str(pathlib.Path(workspace_path, 'params.json')), mode='r') as fp:
        params = json.load(fp)
        videoInfo =  [strms for strms in params['streams'] if strms["index"] == 0][0]
        audioInfo =  [strms for strms in params['streams'] if strms["index"] == 1][0]

        # r_frame_rate -> lowest frame reate
        # avg_frame_rate -> total frame / video duration
        frameRate = int(videoInfo["r_frame_rate"].split("/")[0])

    return frameRate
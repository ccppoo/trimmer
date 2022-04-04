import pathlib
import subprocess
from audiotsm import phasevocoder
from audiotsm.io.wav import WavReader, WavWriter
from scipy.io import wavfile
import numpy as np
import math
from utils import *
from codecs_config import *
from args_parsing import get_args
from youtube_stuffs import *
from ffmpeg_stuffs import *
from video_source import get_video_source
from video_info import get_video_info

TEMP = "TEMP"

WORK_DIR = None

def main():
    args = get_args()
    make_directory(pathlib.Path(os.getcwd(), TEMP))
    ############ Setting globals ############
    '''
    Default

    input_file='test.mkv'
    output_file=None
    url=None

    frame_margin = 1.0
    frame_quality = 3
    frame_rate=30.0

    sample_rate=44100.0
    silent_speed=4.0
    silent_threshold=0.03
    sounded_speed=1.0
    '''

    frameRate = args.frame_rate
    SAMPLE_RATE = int(args.sample_rate)
    SILENT_THRESHOLD = args.silent_threshold
    FRAME_SPREADAGE = args.frame_margin
    NEW_SPEED = [args.silent_speed, args.sounded_speed]
    FRAME_QUALITY = args.frame_quality    
    AUDIO_FADE_ENVELOPE_SIZE = 400 # smooth out transitiion's audio by quickly fading in/out (arbitrary magic number whatever)


    videoSource = args.url or args.input_file 
    videoName, INPUT_FILE = get_video_source(videoSource)

    # exit()
    OUTPUT_FILE = get_video_output_path(args.output_file, INPUT_FILE)

    WORK_DIR = f"{videoName}-{get_date()}"
    
    WORK_DIR = get_workspace_name(WORK_DIR)
    WORKSPACE_PATH = make_workspace(WORK_DIR)

    TEMP_FOLDER = make_workspace(str(pathlib.Path(WORK_DIR, TEMP)))
    TEMP_NEW_FOLDER = make_workspace(str(pathlib.Path(WORK_DIR, "new" + TEMP)))

    ############ Logic ############

    frameRate = get_video_info(INPUT_FILE, WORKSPACE_PATH)
    frameRate = int(frameRate)

    

    AUDIO_FADE_ENVELOPE_SIZE = int(AUDIO_FADE_ENVELOPE_SIZE * (frameRate/30))
    print(f'{AUDIO_FADE_ENVELOPE_SIZE=}')

    """
    -옵션:stream_specifier
        -v | -V : video
        -a : audio
        -s : subtitle
        -d : data
        -t : attachments
        
    -i input_url(file)

    -qscale q           use fixed quality scale (VBR)
        -q[:stream_specifier] q (output,per-stream)
        -qscale[:stream_specifier] q (output,per-stream)
        1~51 값입력, 애니의 경우 25, 영화의 경우 30이 적당하다고 함 (낮을 수록 고화질 고용량)

    -hide_banner
        이거는 저작권, 빌드 옵션, 라이브러리 버전, 등 정보 원래는 출력되는데 가리는 옵션

    이 명령어는 영상의 프레임을  "frame%06d.jpg" 라는 포멧으로 추출하라는 의미다

    qscale를 50으로 할 때 같은 이미지 크기, 비트, 픽셀수는 같지만 용량은 39.4KB
    qscale를 1 할 때 같은 이미지 크기, 비트, 픽셀수는 같지만 용량은 157KB
    정도로 대략 3~4배 차이를 보여줌
    """
    processtr = make_process("ffmpeg -i", INPUT_FILE, "-qscale:v", str(FRAME_QUALITY), pathlib.Path(TEMP_FOLDER, "frame%06d.jpg"), "-hide_banner")
    print(f"{processtr=}")
    subprocess.call(processtr)

    """
    -ac
        Set the number of audio channels(돌비 5.1, 7.1 채널 이런거 말하는 거임 소리가 나는 방향).
        For input streams this option only makes sense for audio grabbing devices and raw demuxers and is mapped to the corresponding demuxer options.

    -ab 
        bitrate         audio bitrate (please use -b:a)

    -ar 
        rate            set audio sampling rate (in Hz)
    
    -vn
                        disable video
    
    오디오 비트레이트 160kb, 2 채널, 오디오 샘플링 레이트 44100.0, 비디오 없이 audio.wav 파일로 저장
    """
    processtr = make_process("ffmpeg -i", INPUT_FILE, "-ab 160k -ac 2 -ar", str(SAMPLE_RATE), "-vn", pathlib.Path(WORKSPACE_PATH, "audio.wav"))
    print(f"{processtr=}")
    subprocess.call(processtr, shell=False)

    """
    이 아래부터는 영상, 소리 작업하는 코드

    """
    
    '''
    RETURNS 
    rate : int
        Sample rate of WAV file.
    data : numpy array (np.ndarray)
        Data read from WAV file. Data-type is determined from the file;
        see Notes.  Data is 1-D for 1-channel WAV, or 2-D of shape
        (Nsamples, Nchannels) otherwise. If a file-like input without a
        C-like file descriptor (e.g., :class:`python:io.BytesIO`) is
        passed, this will not be writeable.
    '''

    # (오디오 샘플 레이트), (오디오 데이터 - np.array로 되어 있음)
    sampleRate, audioData = wavfile.read(str(pathlib.Path(WORKSPACE_PATH, "audio.wav")))
    
    maxAudioVolume = getMaxVolume(audioData)
    audioSampleCount = audioData.shape[0]

    videoLength = audioData.shape[0] / sampleRate

    # (프레임당 오디오 샘플 레이트) = (오디오 샘플레이트) / (앞으로 만들어질 영상 프레임레이트)
    samplesPerFrame = sampleRate/frameRate

    # 오디오 프레임 = (오디오 샘플 개수 추출한것) / (영상 프레임당 오디오 샘플 레이트)
    # 여기서 필요한 오디오의 개수를 가져오는 듯
    audioFrameCount = int(math.ceil(audioSampleCount/samplesPerFrame)) # 287

    hasLoudAudio = np.zeros((audioFrameCount))

    """
    1. 

    """
    # 비디오 한 프레임당 만들 소리 샘플링
    for i in range(audioFrameCount):
        # 앞으로 만들 영상 소리 배열 인덱스 만드는 것

        # 시작 (배열의) 인덱스
        start = int(i*samplesPerFrame)  #  44,100(Hz) / 30(fps)

        # 끝나는 (배열의) 인덱스
        end = min(int((i+1)*samplesPerFrame),audioSampleCount)

        # 원본 오디오에서 그만큼을 잘라온다
        audiochunks = audioData[start:end]

        # 잘라온 오디오 중에서 가장 큰 소리(진폭이기 때문에 절댓값을 기준으로 최댓값을 찾음)
        # maxAudioVolume은 전체 오디오 중에서 가장 큰 값을 의미한다
        # maxchunksVolume는 한 프레임에 들어가는 오디오 샘플링 중에서 가장 큰 소리를 전체 오디오 중 가장 큰 소리로 나눈 것이다.
        maxchunksVolume = float(getMaxVolume(audiochunks))/maxAudioVolume

        # SILENT_THRESHOLD, 즉 소리 없음의 기준점인 0.03 보다 크면 LoudAudio라고 보는 것이다.
        # 즉, LoudAudio는 소리지르는 그런 장면이 아닌, 살릴 장면을 고르는 것이다.
        # hasLoudAudio[i] = 1 이면 그 장면은 안 잘리는 것
        if maxchunksVolume >= SILENT_THRESHOLD:
            hasLoudAudio[i] = 1


    """
    2. 
    
    """

    # 이거는 초기 값 [0,0,0] 넣은 것(어차피 안 씀)
    chunks = [[0,0,0]]
    # 여기서 아마 소리가 작아도 가져와야할 화면을 파악하는 것 같다.
    # 소리 없는 부분(앞 마진) + 소리 있는 부분 + 소리 없는 부분(뒷 마진) 이런식으로 만드는 것
    # 즉, 기본값 1.0은 소리가 있는 프레임 앞 뒤로 1 프레임 씩 소리 없는 프레임으로 붙여서 약간의 공백을 만드는 것
    shouldIncludeFrame = np.zeros((audioFrameCount))
    for i in range(audioFrameCount):
        # FRAME_SPREADAGE == frame_margin == 1.0 이라는 것

        # 영상 첫 부분 감안해서 max(0, ..) 함
        start = int(max(0,i-FRAME_SPREADAGE))
        # 영상 마지막 부분 감안해서 min(audioFrameCount, .. ) 함
        end = int(min(audioFrameCount,i+1+FRAME_SPREADAGE))

        # 위에서 찾은 소리 있는 부분 중에서 소리 있는지 찾는 것 같음(왜냐면 어차피 다 1 또는 0 임)
        # 그리고 shouldIncludeFrame 이름처럼 꼭 저장할 프레임을 여기서 선별
        shouldIncludeFrame[i] = np.max(hasLoudAudio[start:end])
        
        if (i >= 1 and shouldIncludeFrame[i] != shouldIncludeFrame[i-1]): # Did we flip?
            # chunks 구조는... 
            # [ 
            #   <chuncks에서 가장 최근의 프레임에서 2번째 값>, 
            #   <현재 for-loop의 프레임 인덱스>,
            #   <이전 프레임 소리 유무(0, 1)>
            # ] 추가
            chunks.append([chunks[-1][1], i ,shouldIncludeFrame[i-1]])

    # 영상의 맨 마지막 프레임
    chunks.append([chunks[-1][1], audioFrameCount, shouldIncludeFrame[i-1]])
    # [[0,0,0]]이거 빼고 뒤에 있는 것들 가져옴
    chunks = chunks[1:]

    # audioData.shape[1]은 채널 수를 의미함, 오디오를 넣어야 하느니...
    outputAudioData = np.zeros((0,audioData.shape[1]))
    outputPointer = 0
    lastExistingFrame = None

    '''
    TODO: 
        여기서 시간 많이 걸림 (CPU 점유율도 높지도 않고 스레드 사용안해서 많이 느림)
        필요한 프레임만 가져와서 다른 이름으로(앞에 new 붙이는거) 복사하는 건데
        I/O 작업이다보니 코어만 2개 이상 있으면 시간 단축 가능할 듯

        소리를 단위로 chunk를 나누니깐 프레임이 "소리 chunk"에 따라 나뉘어지면 상관이 없음
        그래서 아래 for문은 chunk가 잘못해서 절단면이 크게 일어나는 것을 고려하지 않고
        병렬로 진행해도 큰 상관은 없을 것,
        단 프레임 숫자 붙이기가 문제다
    '''
    for chunk in chunks:
        # 살려야할 오디오+프레임을 프레임 기준으로 정했기 때문에
        # chunk[0]*samplesPerFrame를 해서, 프레임 한 개 + 오디오 레이트 개수 만큼 가져오는 것
        audioChunk = audioData[int(chunk[0]*samplesPerFrame):int(chunk[1]*samplesPerFrame)]
        
        sFile = str(pathlib.Path(WORKSPACE_PATH, "tempStart.wav"))
        eFile = str(pathlib.Path(WORKSPACE_PATH, "tempEnd.wav"))

        # 우선 start.wav을 저장함
        wavfile.write(sFile, SAMPLE_RATE, audioChunk)
        
        # start.wav 저장한 걸 다시 읽고
        with WavReader(sFile) as reader:
            # end.wav에 다시 음성 파일을 씀
            with WavWriter(eFile, reader.channels, reader.samplerate) as writer:
                # 음성파일을 먼저 만들고, 만약에 배속을 한다? 그건 numpy로 할게 아니라
                # 전문 라이브러리(audiotsm)한테 시키는 거임
                tsm = phasevocoder(reader.channels, speed=NEW_SPEED[int(chunk[2])])
                tsm.run(reader, writer)
        
        # 배속을 했건 안했건 처리된 음성 파일을 다시 읽어옴
        _, alteredAudioData = wavfile.read(eFile)
        # shape[0]은 샘플링 개수 (그래서 'leng'th)
        leng = alteredAudioData.shape[0]
        # 소리 샘플 저장할 배열 위치 시작:outputPointer, 끝:endPointer
        endPointer = outputPointer + leng
        # 결과물로 나오는 영상의 소리가 담긴 outputAudioData에 maxAudioVolume(3368.0)를 나눈 np.array를 이어서 붙임
        outputAudioData = np.concatenate((outputAudioData, alteredAudioData/maxAudioVolume))

        #outputAudioData[outputPointer:endPointer] = alteredAudioData/maxAudioVolume -> 이건 원본에 있던거

        # smooth out transitiion's audio by quickly fading in/out
        
        # AUDIO_FADE_ENVELOPE_SIZE (400) 이건 제작자가 임의로 정한 것
        if leng < AUDIO_FADE_ENVELOPE_SIZE:
            # 소리 샘플링 개수가 400개보다 작으면 제거한다
            # test.mkv의 경우 여기서 프레임당 소리 샘플이 1,465개다
            # 즉 30fps니깐 1/30초 = 0.03초에다가 한 프레임당 1,465개니깐
            # 400개 보다 적으면 0.01초에 해당되는 부분이다보니깐 아래 개발자가 메모로 적은 0.01 초보다 짧다는 의미가 됨
            outputAudioData[outputPointer:endPointer] = 0 # audio is less than 0.01 sec, let's just remove it.
        else:
            # AUDIO_FADE_ENVELOPE_SIZE 길이의 np.range 만듦
            # np.arange(5)/5 --> array([0. , 0.2, 0.4, 0.6, 0.8])
            premask = np.arange(AUDIO_FADE_ENVELOPE_SIZE)/AUDIO_FADE_ENVELOPE_SIZE
            
            # premask를 2차원으로 만들고, 채널이 2개니깐 2번 반복, 축이 하나 더 있으니깐 axis=1
            # 이렇게 하면 wavfile.read 해서 return 값으로 받은 audioData와 같은 모양으로 됨
            mask = np.repeat(premask[:, np.newaxis],2,axis=1) # make the fade-envelope mask stereo

            # 시작 지점 ~ 시작 지점 + AUDIO_FADE_ENVELOPE_SIZE 하면 소리 점차 커짐
            outputAudioData[outputPointer:outputPointer+AUDIO_FADE_ENVELOPE_SIZE] *= mask

            # 반대로 마지막 지점 - AUDIO_FADE_ENVELOPE_SIZE(샘플링 개수) ~ 마지막 지점 해서 소리 점차 작아짐
            outputAudioData[endPointer-AUDIO_FADE_ENVELOPE_SIZE:endPointer] *= 1-mask

        '''
        여기는 소리 작업(속도 빠르게 하는것) + 그 소리가 들려질 장면(이미지) 만드는 작업
        '''
        # 프레임에서 시작하는 소리 샘플링의 시작 지점과 끝 지점
        startOutputFrame = int(math.ceil(outputPointer/samplesPerFrame))
        endOutputFrame = int(math.ceil(endPointer/samplesPerFrame))

        for outputFrame in range(startOutputFrame, endOutputFrame):
            # chunk[0] == 프레임의 인덱스
            # chunk[2] == 이전 소리의 프레임(1 or 0)
            # 소리 빨리할건지 안 할건지 여기서 다시 재조정
            inputFrame = int(chunk[0] + NEW_SPEED[int(chunk[2])]*(outputFrame-startOutputFrame) )

            # 영상에 보일 새로운 프레임(이미지) 복사함
            didItWork = copyFrame(inputFrame,outputFrame, TEMP_FOLDER, TEMP_NEW_FOLDER)

            if didItWork:
                lastExistingFrame = inputFrame
            else:
                copyFrame(lastExistingFrame,outputFrame, TEMP_FOLDER, TEMP_NEW_FOLDER)

        # 다음 프레임 위치 재조정
        outputPointer = endPointer

    sFile = str(pathlib.Path(WORKSPACE_PATH, "tempStart.wav"))
    eFile = str(pathlib.Path(WORKSPACE_PATH, "tempEnd.wav"))
    os.remove(sFile)
    os.remove(eFile)

    # 새로 다듬은 소리 파일 위치 audioNew.wav, SAMPLE_RATE == 44100Hz, 소리 데이터(np.array) 씀
    wavfile.write(str(pathlib.Path(WORKSPACE_PATH,"audioNew.raw")),SAMPLE_RATE,outputAudioData)

    '''
    outputFrame = math.ceil(outputPointer/samplesPerFrame)
    for endGap in range(outputFrame,audioFrameCount):
        copyFrame(int(audioSampleCount/samplesPerFrame)-1,endGap, TEMP_FOLDER)
    '''

    """
    -strict            <int>        ED.VA...... how strictly to follow the standards (from INT_MIN to INT_MAX) (default normal)
        very            2            ED.VA...... strictly conform to a older more strict version of the spec or reference software
        strict          1            ED.VA...... strictly conform to all the things in the spec no matter what the consequences
        normal          0            ED.VA......
        unofficial      -1           ED.VA...... allow unofficial extensions
        experimental    -2           ED.VA...... allow non-standardized experimental things

    잘라낸 화면이랑 소리를 합치는 명령어

    영상 길이(초) * framerate(30fps) * (한 프레임에 들어갈 소리 샘플링 개수) 
        == 
            (audioNew.raw 시간) * (모든 소리 샘플링 개수)
    """

    # 이런 메세지가 뜬다 --> 스레드 큐 옵션 늘리기?
    # [image2 @ 000002384582d900] Thread message queue blocking; consider raising the thread_queue_size option (current value: 8)
    """
    TODO:
        이 마지막 작업이 2.2 배속으로 밖에 인코딩을 못하던데
        이걸 H/W or GPU 가속을 할 수 있는 지 확인하는 스크립트가 필요함
    """
    processtr = make_process(
        "ffmpeg", "-framerate", str(frameRate), "-i", 
        pathlib.Path(TEMP_NEW_FOLDER, "newFrame%06d.jpg"), "-i", 
        pathlib.Path(WORKSPACE_PATH, "audioNew.raw"), "-strict -2", OUTPUT_FILE
    )
    subprocess.call(processtr, shell=False)

    # make this another option
    # deletePath(WORKSPACE_PATH)

if __name__ == '__main__':
    main()
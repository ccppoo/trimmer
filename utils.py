from typing import List
from os import getcwd, path
import os, sys
import pathlib
import yaml
import datetime
import shutil
import requests

'''
subprocess로 경로 넘길 떄는 raw string 으로 반환해야한다!!!!!!!!

'''

OS = sys.platform
DEFAULT_CHANGED_NAME = "_modified"

__all__ = [
    "OS",
    "make_process",
    "open_yaml",
    "make_directory",
    "get_workspace_name",
    "make_workspace",
    "reflectIncrement",
    "resolve_full_path",
    "get_date",
    "deletePath",
    "resolve_relative_path",
    "get_video_output_path",
    "validate_url"
]

yaml_suffix = ['yaml', 'yml']

def make_process(*args):
    # TODO : 
    '''
    usage is same as subprocess.call/run/Popen some commands are changed
    UNIX : 'ls' <--> win32 'dir'
    and file paths are changed again fulfilling OS types 
    '''

    return ' '.join([str(arg) for arg in args])

def open_yaml(path_to_yaml : str) -> dict:
    
    path_to_yaml = pathlib.Path(path_to_yaml)

    if not path.exists(path_to_yaml):
        
        dirname = path.dirname(path_to_yaml)
        basename = path.basename(path_to_yaml)

        msg = f'''
        Yaml File does not exists!

        directory : {dirname if dirname else os.getcwd() }
        file : {basename}
        '''

        print(msg)
        exit(-1)
    
    if not path.isfile(path_to_yaml) and not path_to_yaml.endswith(yaml_suffix):
        msg = f'''
        Given path is not a valid .yaml/.yml file!

        directory : {dirname if dirname else os.getcwd() }
        file : {basename}
        '''

        print(msg)
        exit(-1)

    try :
        with open(path_to_yaml, mode='r') as fp:
            yaml_obj = yaml.safe_load(fp)
    except yaml.YAMLError as parse_error:
        print('\n' , parse_error, '\n')
        exit(-1)
    
    return yaml_obj

def get_date() -> str:
    """
    Returns:
        example : 2022-04-12
    """
    
    return datetime.datetime.now().strftime("%Y-%m-%d")

def make_directory(path_ : os.PathLike) -> bool:
    if not os.path.exists(path_):
        os.mkdir(path_)
        return True
    return False

def get_workspace_name(path_ : os.PathLike) -> pathlib.Path:
    '''
    디렉토리 만드는게 아니라 이름 만들어주는 함수임

    작업 할 영상 만들 폴더를 만들고
    이름이 중복(같은 이름을 가진 영상의 경우)되면 숫자 encrement
    폴더 경로 반환하는 것
    '''
    # path_ = str(pathlib.Path("TEMP", path_))

    dir = dirname if (dirname := os.path.dirname(path_)) else pathlib.Path(os.getcwd(), "TEMP")
    dir = str(dir)
    full_path = pathlib.Path(dir, path_)

    if not os.path.isdir(str(full_path)):
        return full_path

    if os.path.exists(str(full_path)):
        # print(f"{reflectIncrement(path_, dir)=}")
        return pathlib.Path(dir, reflectIncrement(path_, dir))
    
    return pathlib.Path(dir, path_)

def make_workspace(path_ : pathlib.Path) -> pathlib.Path:
    
    try:
        os.mkdir(path = path_)

    except Exception as e:
        # 아마도 OS 에러
        path_ = str(path_)
        err_msg  = f"\nError while making directory : {path_}\n"
        err_msg += f"dir : {os.path.dirname(path_)}\n"
        err_msg += f"basename : {os.path.basename(path_)}\n"
        err_msg += "=== trace back ===\n\n"
        err_msg += str(e)
        raise Exception(err_msg)
    
    return path_

def reflectIncrement(base : os.PathLike, in_folder: os.PathLike = None) -> pathlib.Path:
    '''
    in_folder가 None일 경우 base에서 dir 찾음, base가 상대경로일 경우 cwd로 가정하고 동작

    base가 fullpath인 동시에 in_folder가 None이 아닐 경우 in_folder를 우선으로 사용함 
    '''

    base_dir = in_folder if in_folder else (dir_ if (dir_ := os.path.dirname(base)) else os.getcwd())
    base = os.path.basename(base)
    full_path = str(pathlib.Path(base_dir, base))

    isFile = len(base.split('.')) >1

    format_1 = "{}_{}.{}"
    format_2 = "{}_{}"
    n = 1
    if isFile:
        if not os.path.exists(full_path):
            return pathlib.Path(base_dir, base)
        bbase, ext = base.split('.')
        # while os.path.exists(f"{bbase}_{n}.{ext}"):
        while os.path.exists(str(pathlib.Path(base_dir, format_1.format(bbase, n, ext)))):
            n += 1
        if n:
            # return pathlib.Path(base_dir, f"{bbase}({n}).{ext}")
            return pathlib.Path(base_dir, format_1.format(bbase, n, ext))

    if not isFile:
        if not os.path.exists(full_path):
            return pathlib.Path(base_dir, base)
        # while os.path.exists(f"{base}({n})"):
        while os.path.exists(str(pathlib.Path(base_dir,format_2.format(base, n)))):
            n += 1
        if n:
            # return pathlib.Path(base_dir, f"{base}({n})")
            return pathlib.Path(base_dir, format_2.format(base, n))

    # return pathlib.Path(base_dir+f"({n})")
    return pathlib.Path(format_2.format(base_dir, n))

def deletePath(s): # Dangerous! Watch out!
    
    if OS:
        pass
    
    try:
        shutil.rmtree(s,ignore_errors=False)
    except OSError:  
        print ("Deletion of the directory %s failed" % s)
        print(OSError)

def validate_url(url) -> bool:
    
    try:
        requests.get(url)
    except requests.ConnectionError as exception:
        return False
    else:
        return True

def get_video_output_path(output_path : os.PathLike, source_path : os.PathLike) -> os.PathLike:

    if not output_path:
        src_dir = os.path.dirname(source_path)
        src = os.path.basename(source_path)
        filename, ext = src.split('.')[:-1], src.split('.')[-1]
        # in case of file name having dot in names like "my.video.mkv"
        filename = filename[0] if len(filename) > 1 else '.'.join(filename)
        filename = f"{filename + DEFAULT_CHANGED_NAME}.{ext}"
        return reflectIncrement(filename, src_dir)

    if os.path.exists(output_path):
        raise Exception(f"\nfile already exists : {output_path}")

    return pathlib.Path(output_path)

def resolve_full_path(path_ : str) -> str:
    pass

def resolve_relative_path(path_ : str) -> str:
    pass

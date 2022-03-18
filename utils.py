from typing import List
from os import getcwd, path
import os, sys
import pathlib
import yaml

'''
subprocess로 경로 넘길 떄는 raw string 으로 반환해야한다!!!!!!!!

'''

OS = sys.platform

__all__ = [
    "OS",
    "open_yaml",
    "reflectIncrement",
    "resolve_full_path",
    "get_date",
    "resolve_relative_path"
]

yaml_suffix = ['yaml', 'yml']

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
    import datetime
    return datetime.datetime.now().strftime("%Y-%m-%d")

def reflectIncrement(base : os.PathLike, in_folder: os.PathLike = None) -> pathlib.Path:
    '''
    in_folder가 None일 경우 base에서 dir 찾음, base가 상대경로일 경우 cwd로 가정하고 동작

    base가 fullpath인 동시에 in_folder가 None이 아닐 경우 in_folder를 우선으로 사용함 
    '''

    base_dir = in_folder if in_folder else (dir_ if (dir_ := os.path.dirname(base)) else os.getcwd())
    base = os.path.basename(base)

    isFile = len(base.split('.')) >1

    n = 1
    if isFile:
        if not os.path.exists(base):
            return pathlib.Path(base_dir, base)
        bbase, ext = base.split('.')
        while os.path.exists(f"{bbase}({n}).{ext}"):
            n += 1
        if n:
            return pathlib.Path(base_dir, f"{bbase}({n}).{ext}")

    if not isFile:
        if not os.path.exists(base):
            return pathlib.Path(base_dir, base)
        while os.path.exists(f"{base}({n})"):
            n += 1
        if n:
            return pathlib.Path(base_dir, f"{base}({n})")

    return pathlib.Path(base_dir+f"({n})")

def resolve_full_path(path_ : str) -> str:
    pass

def resolve_relative_path(path_ : str) -> str:
    pass

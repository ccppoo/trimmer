from typing import Tuple, TypeVar, Union
from urllib.parse import urlparse

from utils import validate_url
from youtube_stuffs import *

ValidURL = TypeVar("ValidURL", str, bytes)
VideoName = TypeVar("VideoName", str, bytes)

__pure_name = lambda x : '.'.join((pathlib.Path(x).name).split('.')[:-1])

def __uri_validator(source):
    try:
        result = urlparse(source)
        return all([result.scheme, result.netloc])
    except:
        return False

def get_video_source(source : Union[ValidURL,  os.PathLike]) -> Tuple[VideoName, os.PathLike]:
    # local_file or url

    isURL = __uri_validator(source)

    source_path : str  = None
    base_path : str = None

    if isURL:
        try:
            source_path = download_from_Youtube(source)
        except:
            raise ValueError(f"\nThis is not a valid URL : {source}")
        
    if not isURL:
        dir_path = dir_path if (dir_path := os.path.dirname(source)) else os.getcwd() 
        base_path = os.path.basename(source)

        if not os.path.isfile(source):
            raise ValueError(f"\nThis is not a valid File : {pathlib.Path(dir_path, base_path)}")
    
        source_path = pathlib.Path(dir_path, base_path)
    
    return __pure_name(source_path) , str(source_path)
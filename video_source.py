from utils import validate_url
from youtube_stuffs import *

def get_video_source(url = None, local_file : os.PathLike = None) -> os.PathLike:

    if not any([url, local_file]):
        raise ValueError("no input file or youtube URL source provided")
    
    if all([url, local_file]):
        raise ValueError("You should put choose from one source 'URL' or 'Local file'")

    if url:
        if not validate_url(url):
            raise ValueError(f"\nThis is not a valid URL : {url}")
        source_path = download_from_Youtube(url)
    
    if local_file:
        dir_path = dir_path if (dir_path := os.path.dirname(local_file)) else os.getcwd() 
        base_path = os.path.basename(local_file)

        if not os.path.isfile(local_file):
            raise ValueError(f"\nThis is not a valid File : {pathlib.Path(dir_path, base_path)}")
    
        source_path = pathlib.Path(dir_path, base_path)

    return source_path
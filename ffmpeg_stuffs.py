import pathlib
import numpy as np
import os
import shutil

def getMaxVolume(s):
    maxv = float(np.max(s))
    minv = float(np.min(s))
    return max(maxv,-minv)

def copyFrame(inputFrame : int ,outputFrame: int, from_ : os.PathLike, to_ : os.PathLike) -> bool:
    src = pathlib.Path(from_, f"frame{inputFrame+1:06d}.jpg")
    dst = pathlib.Path(to_, f"newFrame{outputFrame+1:06d}.jpg")
    
    if not os.path.isfile(src):
        return False
    
    shutil.copyfile(src, dst)
    
    if outputFrame%20 == 19:
        print(str(outputFrame+1)+" time-altered frames saved.")
    
    return True
import numpy as np
import os
import shutil

def getMaxVolume(s):
    maxv = float(np.max(s))
    minv = float(np.min(s))
    return max(maxv,-minv)

def copyFrame(inputFrame : int ,outputFrame: int, at : os.PathLike) -> bool:
    src = at+"/frame{:06d}".format(inputFrame+1)+".jpg"
    dst = at+"/newFrame{:06d}".format(outputFrame+1)+".jpg"
    
    if not os.path.isfile(src):
        return False
    
    shutil.copyfile(src, dst)
    
    if outputFrame%20 == 19:
        print(str(outputFrame+1)+" time-altered frames saved.")
    
    return True
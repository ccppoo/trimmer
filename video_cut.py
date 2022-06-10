from utils import *
import subprocess

INPUT_FILE = "2022-05-19.mkv"
OUTPUT_FILE = f"2022-05-19_cut.mkv"

FROM = "00:08:50"
TO = "00:47:20"

processtr = make_process(f"ffmpeg -ss {FROM} -to {TO}  -i {INPUT_FILE} -c copy {OUTPUT_FILE}")
print(f"{processtr=}")
subprocess.call(processtr)

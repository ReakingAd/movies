from enum import Enum, unique
import os
import queue
import random
import re
import sys
import threading
import time
import subprocess

for attempt in range(3):
    if attempt == 2:
        break
    print(f"Attempt {attempt + 1}")
else:
    print("Max attempts reached")

if __name__ == '__main__':
    # print(Task_Type.QQMUSIC_SONG)
    # print(Task_Type.QQMUSIC_ALBUM)
    subprocess.run(["shutdown", "/s", "/t", "60"])
    time.sleep(3)
    subprocess.run(["shutdown", "/a"])

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

def shutdown_if_not_cancel():
    try:
        print("60s后关机，按 Ctrl+C 取消：")
        for remaining in [60, 40, 20]:
            print(f"剩余时间{remaining}s")
            time.sleep(20)
        subprocess.run(['shutdown', '/s', '/t', '0'])
    except KeyboardInterrupt:
        print("\n🛑 检测到用户中断，取消关机")
        return
    
if __name__ == '__main__':
    # print(Task_Type.QQMUSIC_SONG)
    # print(Task_Type.QQMUSIC_ALBUM)


    # subprocess.run(["shutdown", "/s", "/t", "60"])
    # time.sleep(3)
    # subprocess.run(["shutdown", "/a"])
    # cancel = input("shuru stop to cancel:")
    # print(cancel)
    # if cancel.lower() == "stop":
    #     # subprocess.run(["shutdown", "/a"])
    #     print("cancel....")
    # TODO: 关机命令有没有一个执行队列？怎么查看?
    shutdown_if_not_cancel()
    # try:
    #     print("60s后关机（按 Ctrl+C 取消）")
    #     for remaining in [60, 40, 20]:
    #         print(f"⏳ 剩余时间：{remaining}s")
    #         time.sleep(20)
    # except KeyboardInterrupt:
    #     print("\n🛑 检测到用户中断，取消关机")
    #     subprocess.run(["shutdown", '/a'])
        
    # print("start shutdown......")
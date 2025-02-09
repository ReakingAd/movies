from enum import Enum
import os
import random
import re
import sys
import time

import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

def task(n):
    time.sleep(n)
    print(f'Task {n} completed')
    return n

def main():
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(task, i) for i in range(10)]

        completed_tasks = 0
        for future in as_completed(futures):
            # result = future.result()
            completed_tasks += 1
            # print(f'Completed tasks: {completed_tasks}, Result: {result}')
            print(f'Completed tasks: {completed_tasks}')

def calc(speed):
    avg = 0
    def inner(speed):
        nonlocal avg
        avg += speed
        return avg
    return inner(speed)

if __name__ == '__main__':
    # 定义颜色常量
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    RESET = '\033[0m'

    # 使用颜色常量来改变打印文字的颜色
    sys.stdout.write(f'\r{GREEN}[{'self.website'}] {'self.video_name'} {RESET}')


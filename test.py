from enum import Enum
import os
import queue
import random
import re
import sys
import threading
import time

def worker(task_queue):
    while True:
        print('in while.............')
        task = task_queue.get()
        if task is None:
            break
        print(f'task={task}')
        print(f'in worker: {task}')
        task_queue.task_done()

if __name__ == '__main__':
    tasks = [1, 2, 3]
    task_queue = queue.Queue()
    
    thread = threading.Thread(target=worker, args=[task_queue,])
    thread.start()

    time.sleep(4)
    for el in tasks:
        task_queue.put(el)

    task_queue.join()
    task_queue.put(None)

    print('all done')


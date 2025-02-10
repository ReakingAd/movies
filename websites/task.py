from enum import Enum, unique
import queue
import threading
import time

from loguru import logger

from qqmusic import QQMusicDownloader
from chabeihu import ChaBeiHuDownloader
from bilibiil import BilibiliDownloader
from xingkongyingshi import XingKongYingShiDownloader

@unique
class TASK_TYPE(Enum):
    QQMUSIC_SONG = 1 # QQ音乐：单曲
    QQMUSIC_ALBUM = 2 # QQ音乐：专辑
    XIONGKONGYINGSHI = 3 # 星空影视
    """
    https://www.chabei1.com/vodplay/87783-1-1.html
    http://www.cbh1.cc/p/172571/40/6270949
    """
    CHANEIHU = 4 # 茶杯狐 TODO：网站改版，代码失效需要更新逻辑
    BILIBILI = 5 # b站

def downloader_factory(type):
    if type == TASK_TYPE.QQMUSIC_SONG or type == TASK_TYPE.QQMUSIC_ALBUM:
        return QQMusicDownloader()
    elif type == TASK_TYPE.XIONGKONGYINGSHI:
        return XingKongYingShiDownloader()
    elif type == TASK_TYPE.CHANEIHU:
        return ChaBeiHuDownloader()
    elif type == TASK_TYPE.BILIBILI:
        return BilibiliDownloader()

def worker(task_queue):
    while True:
        # 【要点1】 (阻塞)从任务队列task_queue中领取一个任务。如果任务队列没有东西。则阻塞在这里等待任务
        task = task_queue.get()
        # 【要点2】  直到从任务队列中拿到的任务是 None 标识位，标识主线程已经没有要执行的任务了，这里可以跳出 while 循环了。
        if task is None:
            break
        dlr = downloader_factory(task['type'])
        if task['type'] == TASK_TYPE.QQMUSIC_SONG:
            dlr.download_song(task['target'])
        elif task['type'] == TASK_TYPE.QQMUSIC_ALBUM:
            dlr.download_album(task['target'])
        elif task['type'] == TASK_TYPE.XIONGKONGYINGSHI:
            dlr.download(task['target'])
        elif task['type'] == TASK_TYPE.CHANEIHU:
            dlr.download(task['target'])
        elif task['type'] == TASK_TYPE.BILIBILI:
            dlr.download(task['target'])
        else:
            logger.error(f'未找到下载器 {task['type']}')
        # 【要点3】 通知任务队列 task_queue 当前任务完成
        task_queue.task_done()

"""
线程、任务控制逻辑：
- 主线程创建子线程 thread, 创建任务队列 task_queue
- 主线程是生产者，向任务队列中添加任务。子线程是消费者，从任务队列中领取任务
- 主线程每put() 一次，计数+1， 子线程每 task_done() 一次，计数 -1。
    主线程task_queue.join()就在阻塞等待 put()调用次数 == task_done() 的调用次数相等，才继续执行后续代码
- 主线程再向队列 put() 一个任务叫做 None 作为标志位。紧接着thread.join() 阻塞等待子线程代码执行完毕
- 子线程领取到任务 None，跳出 while True 循环，随即子线程代码全部执行完毕。主线程可以继续执行thread.join()后面的代码
- 流程完毕
"""
def run(tasks):
    task_queue = queue.Queue()
    thread = threading.Thread(target=worker, args=[task_queue,]) # 下载线程，负责将任务队列的任务一个一个的下载下来
    thread.start()

    for task in tasks:
        task_queue.put(task)

    # 【要点4】 (阻塞) 等待任务队列task_queue中目前已有的任务都被消费完毕
    task_queue.join()
    # 【要点5】 再次向 task_queue 推送结束标志位 None，方便子线程的worder函数跳出 while True循环。
    # worder 跳出循环后才能真正执行完毕，子线程才能退出
    task_queue.put(None) # 
    # 【要点6】 (阻塞) 主线程会阻塞在这里，等待 thread 子线程中的任务执行完毕
    thread.join() 
    print("所有任务执行完毕")


if __name__ == '__main__':
    tasks = [
        {'type': TASK_TYPE.QQMUSIC_SONG, 'target': '0015BszJ09xZ2z'},
        {'type': TASK_TYPE.QQMUSIC_ALBUM, 'target': '0046jew92EyhAb'},
        {'type': TASK_TYPE.XIONGKONGYINGSHI, 'target': 'https://www.xkvvv.com/play/397/1/1/'},
        # {'type': TASK_TYPE.CHANEIHU, 'target': 'https://www.chabei1.com/vodplay/87783-1-1.html'},
        {'type': TASK_TYPE.BILIBILI, 'target': 'https://www.bilibili.com/video/BV16A411W7SQ'},
    ]
    run(tasks)
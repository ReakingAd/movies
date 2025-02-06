from enum import Enum, unique
import queue
import threading

from qqmusic import QQMusicDownloader
from chabeihu import ChaBeiHuDownloader
from xingkongyingshi import XingKongYingShiDownloader
# from websites.xingkongyingshi import XingKongYingShiDownloader

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

def downloader_factory(type):
    if type == TASK_TYPE.QQMUSIC_SONG or type == TASK_TYPE.QQMUSIC_ALBUM:
        return QQMusicDownloader()
    elif type == TASK_TYPE.XIONGKONGYINGSHI:
        return XingKongYingShiDownloader()
    elif type == TASK_TYPE.CHANEIHU:
        return ChaBeiHuDownloader()

def worker(task_queue):
    while True:
        task = task_queue.get()
        print(task)
        if task == None:
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

def run(tasks):
    task_queue = queue.Queue()
    thread = threading.Thread(target=worker, args=[task_queue,]) # 下载线程，负责将任务队列的任务一个一个的下载下来
    thread.start()

    for task in tasks:
        task_queue.put(task)
    
    task_queue.join()
    task_queue.put(None)
    print("All tasks have been done......")


if __name__ == '__main__':
    tasks = [
        # {'type': 'QQMusic Song', 'target': '000KHITg34Ffid'},
        # {'type': 'QQMusic Album', 'target': '0046jew92EyhAb'},
        # {'type': 'xingkongyingshi', 'target': 'https://www.xkvvv.com/play/118811/3/1/'},
        # {'type': TASK_TYPE.XIONGKONGYINGSHI, 'target': 'https://www.xkvvv.com/play/397/1/1/'},
        {'type': TASK_TYPE.CHANEIHU, 'target': 'https://www.chabei1.com/vodplay/87783-1-1.html'},
        # {'type': TASK_TYPE.CHANEIHU, 'target': 'http://www.cbh1.cc/p/172571/40/6270949'},
    ]
    run(tasks)
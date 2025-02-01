import queue
import threading

from qqmusic import QQMusicDownloader

# 歌曲
def song_worker(task_queue):
    while True:
        song_id = task_queue.get()
        if song_id == None:
            break
        dlr = QQMusicDownloader()
        dlr.download_song(song_id)
        task_queue.task_done()

# 音乐专辑
def album_worker(task_queue):
    while True:
        album_id = task_queue.get()
        if album_id == None:
            break
        dlr = QQMusicDownloader()
        dlr.download_album(album_id)
        task_queue.task_done()

def run(type, ids):
    task_queue = queue.Queue()

    target_func = {
        'QQMusic Song': song_worker,
        'QQMusic Album': album_worker,
    }
    thread = threading.Thread(target=target_func[type], args=(task_queue,))
    thread.start()
    
    for id in ids:
        task_queue.put(id)
    
    task_queue.join()
    task_queue.put(None)
    print('***All tasks have been done***')
if __name__ == '__main__':
    # type = 'QQMusic Song'
    # song_ids = [
    #     '000KHITg34Ffid', # Death04 (Explicit)
    #     '002cmJ0r3Lvkjy', # Separated
    #     '000Kt7GS3ebcRS', # Truth
    #     '000mWWoW2ql7xP', # The Alarm
    #     '002lcMCu4LhstE', # Godspeed to the Freaks
    #     '000iqHgc4btf19',
    #     '003gdMkd3kJDCi',
    #     '004NbAy41nrYtq',
    #     '003GW7La25VC2B',
    #     '001H9Zif4FQbfr'
    # ]
    type = 'QQMusic Album'
    album_ids = [
        '000f01724fd7TH', # Jay
        '000I5jJB3blWeN', # 范特西
        '004MGitN0zEHpb', # 八度空间
        '000MkMni19ClKG', # 叶惠美
        '003DFRzD192KKD', # 七里香
        '0024bjiL2aocxT', # 十一月的萧邦
        '002jLGWe16Tf1H', # 依然范特西
        '001UP7mW458ipG', # 不能说的秘密 电影原声带
        '002eFUFm2XYZ7z', # 我很忙
        '002Neh8l0uciQZ', # 魔杰座
        '000bviBl4FjTpO', # 跨时代
        '003KNcyk0t3mwg', # 惊叹号
        '003Ow85E3pnoqi', # 十二新作
        '003b9EXT2QU0T7', # 黄俊郎的黑
        '001uqejs3d6EID', # 哎呦，不错哦
        '003RMaRI1iFoYd', # 周杰伦的床边故事
        '0042cH172YJ0mz', # 最伟大的作品
    ]
    run(type, album_ids)
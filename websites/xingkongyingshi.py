from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import queue
import re
import shutil
import sys
import threading
import time
import ffmpeg
from loguru import logger
import requests
# from websites.downloader_base import DownloaderBase
from downloader_base import DownloaderBase

# 星空影视
class XingKongYingShiDownloader():
    def __init__(self):

        log_format = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
        # log_format = "<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>[星空影视]: {message}</level>"
        logger.remove()
        logger.add(sys.stdout, format=log_format) # 添加日志处理器，并指定输出格式

        self.website = '星空影视'
        self.url = None
        self.html = None
        self.m3u8_1_url = None
        self.video_name = None
        self.m3u8_2_url = None
        self.segment_urls = None
        self.max_workers = 5 # 线程池大小
        self.max_retry = 5
        self.retry_delay = 30

        self.workspace = None
        self.m3u8_1_local = None
        self.m3u8_2_local = None
        self.concat_file = None

        self.download_speed = 0 # 下载速度
        self.speed_queue = queue.Queue() # 计算下载速度用到的队列
        #####

    def get_html(self, url):
        try:
            logger.info(f'下载 html')
            rsp = requests.get(url, timeout=5)
            rsp.raise_for_status()
            return rsp.text
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                logger.error('没有权限')
            else:
                logger.error(f'请求失败，状态码：{e.response.status_code}')
        except requests.exceptions.RequestException as e:
            logger.error(f'请求发生错误: {e}')

    def parse_video_name(self):
        pattern = re.compile(r'<span.*?class="hl-infos-title"><a.*?>(.*?)</a><em.*?>(.*?)</em>') 
        rst = re.search(pattern, self.html)
        if rst is not None:
            self.video_name = f'{rst.group(1)}{rst.group(2)}'
            self.video_name = self.video_name.replace('&nbsp;', '')
            logger.info(f'解析出视频名称：【{self.video_name}】')
        else:
            logger.error('未解析出视频名称')

    def parse_m3u8_1_url(self):
        pattern = re.compile(r'https://.*?\.m3u8')
        rst = re.search(pattern, self.html)
        if rst is not None:
            self.m3u8_1_url = rst.group()
            logger.info(f'解析第一个 m3u8 文件的 url')
        else:
            logger.error('解析第一个 m3u8 文件的 url 失败')

    def get_m3u8(self, url, local_file):
        for attempt in range(self.max_retry):
            try:
                rsp = requests.get(url, timeout=5)
                rsp.raise_for_status()
                _path = os.path.join(self.workspace, local_file)
                with open(_path, 'w', encoding='utf-8') as f:
                    f.write(rsp.text)
                break
            except requests.exceptions.Timeout:
                logger.error(f'请求超时, {self.retry_delay}s 后重试')
                time.sleep(self.retry_delay)
            except requests.exceptions.RequestException as e:
                logger.error(f'请求失败：{e}, {self.retry_delay}s 后重试')
                time.sleep(self.retry_delay)
        else:
            logger.error(f'达到最大尝试次数,下载 m3u8 失败')
            raise Exception('下载 m3u8 失败')

    def parse_m3u8_2_url(self):
        file_path = os.path.join(self.workspace, '1.m3u8')
        with open(file_path, 'r') as f:
            text = f.read()
            pattern = re.compile(r'^(\S+m3u8)$', re.MULTILINE)
            rst = re.findall(pattern, text)
            if rst is not None:
                self.m3u8_2_url = self.m3u8_1_url.replace('index.m3u8', rst[0])
                logger.info('解析第二个 m3u8 文件的 url')
            else:
                logger.error('解析第二个 m3u8 文件的 url 失败')

    def parse_segment_urls(self):
        file_path = os.path.join(self.workspace, '2.m3u8')
        with open(file_path, 'r') as f:
            text = f.read()
            pattern = re.compile(r'^(\S+\.ts)$', re.MULTILINE)
            rst = re.findall(pattern, text)
            if rst is not None:
                self.segment_urls = [f"{ re.sub(r'[^/]+$', el, self.m3u8_2_url)}" for el in rst]
                logger.info(f'解析视频碎片 urls')
            else:
                logger.error('解析视频碎片 urls 失败')

    def calc_download_speed(self, new_speed):
        """
        近似计算下载速度的算法：每个线程计算自己的下载速度，再将线程池中所有线程的下载速度相加，
        得到整个线程池的下载速度总和
        """
        queue_len = self.speed_queue.qsize()
        if queue_len >= self.max_workers:
            speed_queue_head = self.speed_queue.get()
            self.download_speed -= speed_queue_head
        self.speed_queue.put(new_speed)
        self.download_speed += new_speed

    def get_segments(self):
        path = os.path.join(self.workspace, 'segments')
        if not os.path.exists(path):
            os.makedirs(path)
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [executor.submit(self.get_segment, url) for url in self.segment_urls]
            
            count_completed = 0
            for future in as_completed(futures):
                count_completed += 1
                percent = count_completed / len(self.segment_urls)
                arrow = '▊' * int(percent * 50)
                spaces = ' ' * (50 - len(arrow))
                curr_thread_download_speed = future.result() / 1000 # 当前线程的下载速度
                self.calc_download_speed(curr_thread_download_speed)
                sys.stdout.write(f'\r[{self.website}] {self.video_name} [{arrow}{spaces}] {percent:.2%} {self.download_speed:.2f} Kb/s ')

    def get_segment(self, url):
        result = re.search(r'[^/]+.ts', url)
        segment_name = result[0]
        for attemp in range(self.max_retry):
            try:
                start_time = time.time()
                rsp = requests.get(url, timeout=5)
                end_time = time.time()
                _path = os.path.join(self.workspace, 'segments', segment_name)
                with open(_path, 'wb') as f:
                    f.write(rsp.content)

                    size = len(rsp.content) # 当前任务的：下载的大小
                    gap = end_time - start_time # 当前任务的：下载耗时
                    speed = size / gap # 当前任务的：下载速度
                    return speed
                break
            except requests.exceptions.RequestException as e:
                if attemp < self.max_retry-1:
                    logger.error(f'下载失败,等待 {self.retry_delay}s 后重试: {url}')
                    time.sleep(self.retry_delay)
                else:
                    logger.error(f'下载达到最大次数。失败 {url} ')
            except IOError as e:
                logger.error(f'写入文件失败：{e}. {url}')
            except Exception as e:
                logger.error(f'未知错误: {e}. {url}')

    def init_workspace(self):
        path = os.path.dirname(__file__)
        self.workspace = os.path.join(path, 'downloads', self.video_name)
        if not os.path.exists(self.workspace):
            os.makedirs(self.workspace)
        self.concat_file = os.path.join(self.workspace, 'concat_list.txt')

    def generate_concat_file(self):
        segments_path = os.path.join(self.workspace, 'segments')
        with open(self.concat_file, 'w', encoding='utf-8') as f:
            for url in self.segment_urls:
                result = re.search(r'[^/]+.ts', url)
                segment_name = result[0]
                f.write(f"file '{os.path.join(segments_path, segment_name)}'\n")

    def merge(self):
        (
            ffmpeg
                .input(self.concat_file, format='concat', safe=0)
                .output(f"{os.path.join(self.workspace, self.video_name)}.mp4", vcodec='copy', acodec='copy')
                .run(quiet=True)
        )

    def clear_workspace(self):
        video_file = os.path.join(self.workspace, f'{self.video_name}.mp4')
        curr_path = os.path.dirname(video_file)
        parent_path = os.path.dirname(curr_path)
        shutil.move(video_file, parent_path)

        new_video_file = os.path.join(parent_path, f'{self.video_name}.mp4')
        if os.path.exists(new_video_file):
            try:
                shutil.rmtree(self.workspace)
                logger.info(f'删除工作临时工作目录')
            except Exception as e:
                logger.error(f'删除临时工作目录出错： {e}')
        else:
            logger.error(f'未在新位置上找到视频文件')

    def clean_segment_urls(self):
        """
        @功能：清理视频碎片的url，讲广告碎片清理掉
        @原理：
            正常视频碎片 7ffa1c76dd4000166.ts
            广告视频碎片 7ffa1c76dd40585652.ts

            观察可知，广告视频碎片的字符串长度 > 正常视频碎片的长度。因此举例来说，如果大部分碎片名称的长度是20，个别碎片名称长度为21，
            那么就可以认为长度是21的碎片就是广告碎片，要清理掉。
        """
        len_dict = {}
        for url in self.segment_urls:
            url_len = len(url)
            if url_len in len_dict:
                len_dict[url_len] += 1
            else:
                len_dict[url_len] = 1

        stadard_len = 0
        count = 0
        for key, value in len_dict.items():
            if value > count:
                count = value
                stadard_len = key

        self.segment_urls = list(filter(lambda url: len(url) == stadard_len, self.segment_urls))

    def download(self, url):
        self.url = url
        self.html = self.get_html(self.url)
        self.parse_video_name()
        self.init_workspace()
        self.parse_m3u8_1_url()
        self.get_m3u8(self.m3u8_1_url, '1.m3u8')
        self.parse_m3u8_2_url()
        self.get_m3u8(self.m3u8_2_url, '2.m3u8')
        self.parse_segment_urls()
        self.clean_segment_urls()
        self.generate_concat_file()
        self.get_segments()
        self.merge()
        self.clear_workspace()

    def download_series(self, series_id):
        """
        @功能 下载剧集
        @参数 剧集id。例如：详情页 https://www.xkvvv.com/detail/106075/ 可知剧集id就是 106075
        """
        series_url = f'https://www.xkvvv.com/detail/{series_id}/'
        series_html = self.get_html(series_url)
        # with open('series.html', 'w') as f:
        #     f.write(series_html)
        pattern = re.compile(r'<a href="(/play.*?)"')
        logger.info(f'解析单集的 url')
        result = re.findall(pattern, series_html)
        episode_queue = queue.Queue()

        for el in result:
            episode_queue.put(f'https://www.xkvvv.com/{el}')

        while not episode_queue.empty():
            episode_url = episode_queue.get()
            logger.info(f'下载单集：{episode_url}')
            self.download(episode_url)


if __name__ == '__main__':
    
    # url = 'https://www.xkvvv.com/play/118482/2/37/'
    url = 'https://www.xkvvv.com/play/115337/3/1/'
    dlr = XingKongYingShiDownloader()
    dlr.url = url
    dlr.download(url)
    # dlr.download_series(106074)

# class XingKongYingShiDownloader(DownloaderBase):
#     def __init__(self):
#         self.website = '星空影视'
#     def parse_film_name(self):
#         pattern = r'hl-infos-title">.*?<a.*?>(.*?)</a>.*?<em.*?>(.*?)</em>'
#         result = re.search(pattern, self.html)
        
#         if result is not None:
#             self.film_name = f'{result.group(1)}{result.group(2)}'.replace('&nbsp;', '')
#         else:
#             logger.error(f'解析电影名错误..') 
#     def parse_urls_video_segment(self):
#         pattern_url = r'#EXTINF:.*?,\s(.*?\.ts)'
#         with open(self.local_m3u8_file_2, 'r') as f:
#             content = f.read()
#             matches = re.finditer(pattern_url, content)
#             self.urls = [re.sub(r'(index|mixed).m3u8', match.group(1), self.url_m3u8_file_2) for match in matches]
#             # self.urls_len = 2083
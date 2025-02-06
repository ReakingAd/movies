
from abc import ABC, abstractmethod
from datetime import datetime
import os
import re
import sys
import time

import ffmpeg
from loguru import logger
import requests

# 基类
class DownloaderBase(ABC):

    website = None # 当前工作的视频网站名称
    path = os.path.dirname(__file__)

    html = '' # 视频网页的html代码
    workspace = '' # 当前影片的工作目录。每个影片都有自己的workspace
    film_name = '' # 电影名
    local_html_file = '' # html本地保存的文件

    url_m3u8_file_1 = '' # 第一个m3u8的 url
    local_m3u8_file_1 = '' # 本地保存的第一个 m3u8 文件
    url_m3u8_file_2 = '' # 第二个 m3u8 文件的url
    local_m3u8_file_2 = '' # 本地保存的第二个 m3u8 文件
    segments = '' # 视频文件保存目录
    concat_list_file = '' # 视频碎片信息汇总，后续用于合并视频
    log_file = '' # 日志文件
    
    max_retry = 5 # 下载最大尝试次数
    retry_delay = 5 # 下载重试的时间间隔

    urls = [] # 从m3u8文件解析出的视频碎片的url。是一个迭代器
    urls_len = None # 视频碎片的个数

    def download(self, url):
        self.get_html(url)
        self.init_current_workspace()
        print(f'>>>>>>>>>> {self.film_name} <<<<<<<<<<')
        self.prase_url_m3u8_file_1()
        self.download_m3u8_file_1()
        self.parse_url_m3u8_file_2()
        self.download_m3u8_file_2()
        self.parse_urls_video_segment()
        self.downloads_videos()
        self.merge_segment()
    
    # 下载第一个 m3u8 文件
    def download_m3u8_file_1(self):
        print(f"[{self.website}] 拉取第一个 m3u8 文件")
        response = requests.get(self.url_m3u8_file_1)
        with open(self.local_m3u8_file_1, 'w') as f:
            f.write(response.text)

    # 解析第一个 m3u8 文件的url
    def prase_url_m3u8_file_1(self):
        print(f'[{self.website}] 解析第一个 m3u8 文件的url')
        pattern_m3u8_1 = r'https:.*?/index.m3u8'
        pattern_m3u8_1_result = re.search(pattern_m3u8_1, self.html)
        self.url_m3u8_file_1 = pattern_m3u8_1_result.group(0).replace('\\', '')
        # print(f"解析出第一个 m3u8 文件的 url：{self.url_m3u8_file_1}")
    
    # 初始化当前影片的工作目录。 
    def init_current_workspace(self):
        self.parse_film_name()
        self.workspace = os.path.join(self.path, 'downloads', self.film_name)
        
        self.log_file = os.path.join(self.workspace, f'{datetime.now().strftime('%Y-%m-%d')}.log')
        logger.add(self.log_file, level="INFO", format="{time} - {level} - {message}")

        if not os.path.exists(self.workspace):
            os.makedirs(self.workspace)
            # print(f'创建影片工作目录完成：{self.workspace}')
        else:
            # print(f'影片工作目录已经存在:{self.workspace}')
            pass
        
        self.local_html_file = f'{self.workspace}/index.html'
        with open(self.local_html_file, 'w', encoding='utf-8') as f:
            f.write(self.html)

        self.local_m3u8_file_1 = os.path.join(self.workspace, 'index.1.m3u8')
        self.local_m3u8_file_2 = os.path.join(self.workspace, 'index.2.m3u8')
        self.segments = os.path.join(self.workspace, 'segments')
        self.concat_list_file = os.path.join(self.workspace, 'concat_list.txt')

    def get_html(self, url):
        print(f'[{self.website}] 拉取 html: {url}')
        response = requests.get(url, timeout=300)
        self.html = response.text

    # 解析第二个 m3u8 文件
    @abstractmethod
    def parse_urls_video_segment(self):
        pass
    @abstractmethod
    def parse_film_name():
        pass

    # 合并视频碎片
    def merge_segment(self):
        (
            ffmpeg
                .input(self.concat_list_file, format='concat', safe=0)
                .output(f"{os.path.join(self.workspace, self.film_name)}.mp4", vcodec='copy', acodec='copy')
                .run()
        )
    # 下载视频碎片
    def downloads_videos(self):
        # print("开始下载视频碎片...")
        index = 0
        total = len(self.urls)
        for url in self.urls:
            # print(f'[{self.website}] 开始下载视频{url}')
            pattern_video_name = r'/([^/]*?)\.(ts|jpeg)'
            result = re.search(pattern_video_name, url)
            filename = result.group(1)
            # ext = result.group(2)
            # print(f"开始下载片段：{url}")
            for attempt in range(self.max_retry):
                try:
                    response = requests.get(url, timeout=30)
                    # print(f"下载完成==========")
                    index += 1
                    percent = index / total
                    arrow = '▊' * int(percent * 50)
                    spaces = ' ' * (50 - len(arrow))
                    sys.stdout.write(f'\r[{self.website}] {self.film_name} [{arrow}{spaces}] {percent:.2%}')
                    # sys.stdout.write(f'\r{self.film_name}:{index}>>>>>{percent:.2%}')
                    break
                except Exception as e:
                    logger.warning(f"失败..{e}")
                    if attempt < self.max_retry - 1:
                        print(f"等待 {self.retry_delay} 秒后重试...")
                        time.sleep(self.retry_delay)
                    else:
                        print(f"已经达到最大尝试次数，下载失败：{url}")
            if not os.path.exists(self.segments):
                os.makedirs(self.segments)
            segment_path = os.path.join(self.segments, f'{filename}.ts')
            with open(segment_path, 'wb') as f, open(self.concat_list_file, 'a', encoding='utf-8') as f_list:
                f.write(response.content)
                f_list.write(f"file '{segment_path}'\n")
                
    
    # 拉取第二个 m3u8 文件
    def download_m3u8_file_2(self):
        print(f"[{self.website}] 拉取第二个 m3u8 文件")
        response = requests.get(self.url_m3u8_file_2)
        with open(self.local_m3u8_file_2, 'w') as f:
            f.write(response.text)

    # 解析第二个 m3u8 文件的 url
    def parse_url_m3u8_file_2(self):
        print(f"[{self.website}] 解析第二个 m3u8 文件的url")
        with open(self.local_m3u8_file_1, 'r') as f:
            text = f.read()
            pattern_m3u8_2 = r'\d.*?.m3u8'
            pattern_m3u8_2_result = re.search(pattern_m3u8_2, text)
            self.url_m3u8_file_2 = self.url_m3u8_file_1.replace('index.m3u8', pattern_m3u8_2_result.group(0))
            # print(f"解析出第二个 m3u8 文件的url：{self.url_m3u8_file_2}")
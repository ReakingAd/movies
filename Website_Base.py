
from abc import ABC, abstractmethod
import os
import re
import time

import ffmpeg
from loguru import logger
import requests
# TODO: log文件夹
# TODO: 工作文件夹
# 基类
class Website_Handler(ABC):
    
    path = os.path.dirname(__file__)
    work_path = '' # 针对下载某个影片的任务，创建工作目录
    download_path = f"{path}/downloads" # 视频文件保存目录
    concat_list_file = f"{path}/concat_list.txt" # 视频碎片信息汇总，后续用于合并视频

    html = ''
    film_name = '' # 电影名
    local_html_file = f"{path}/index.html"
    url_m3u8_file_1 = '' # 第一个m3u8的 url
    local_m3u8_file_1 = f"{path}/index.1.m3u8" # 本地保存的 m3u8 文件1
    url_m3u8_file_2 = '' # 第二个 m3u8 文件的url
    local_m3u8_file_2 = f"{path}/index.2.m3u8" # 本地保存的第二个 m3u8 文件

    max_retry = 5 # 下载最大尝试次数
    retry_delay = 5 # 下载重试的时间间隔

    urls = []

    max_retry = 5 # 下载最大尝试次数
    retry_delay = 5 # 下载重试的时间间隔

    # 解析第二个 m3u8 文件
    @abstractmethod
    def parse_urls_video_segment(self):
        logger.info('开始解析视频碎片的url...')
        pass
    @abstractmethod
    def parse_film_name():
        pass


    def get_html(self, url):
        logger.info(f'开始下载 html: {url}')
        response = requests.get(url)
        if(response.status_code == 200):
            self.html = response.text
            with open(self.local_html_file, 'w', encoding='utf-8') as f:
                f.write(response.text)
                logger.info('下载 html 完成.')
        else:
            logger.error('下载 html 出错.')

    def create_work_path(self):
        self.work_path = f'{self.path}/{self.film_name}'
        if not os.path.exists(self.work_path):
            os.makedirs(self.work_path)
            logger.info(f'创建影片工作目录完成：{self.work_path}')
        else:
            logger.info(f'影片工作目录已经存在:{self.work_path}')

    def download(self, url):
        self.get_html(url)
        self.parse_film_name()
        logger.info(f'>>>>>>>>>>>>>>>>>>>> 开始下载电影：{self.film_name}')
        self.prase_url_m3u8_file_1()
        self.download_m3u8_file_1()
        self.parse_url_m3u8_file_2()
        self.download_m3u8_file_2()
        self.parse_urls_video_segment()
        self.downloads_videos()
        self.merge_segment()
    
    # 合并视频碎片
    def merge_segment(self):
        (
            ffmpeg
                .input(self.concat_list_file, format='concat', safe=0)
                .output(f"{self.path}/{self.film_name}.mp4", vcodec='copy', acodec='copy')
                .run()
        )
    # 下载视频碎片
    def downloads_videos(self):
        logger.info("开始下载视频碎片...")
        for url in self.urls:
            pattern_video_name = r'/([^/]*?)\.(ts|jpeg)'
            result = re.search(pattern_video_name, url)
            filename = result.group(1)
            # ext = result.group(2)
            logger.info(f"开始下载片段：{url}")
            for attempt in range(self.max_retry):
                try:
                    response = requests.get(url, timeout=30)
                    print(f"下载完成==========")
                    break
                except Exception as e:
                    logger.warning(f"失败..")
                    if attempt < self.max_retry - 1:
                        logger.info(f"等待 {self.retry_delay} 秒后重试...")
                        time.sleep(self.retry_delay)
                    else:
                        logger.info(f"已经达到最大尝试次数，下载失败：{url}")

            with open(f"{self.download_path}/{filename}.ts", 'wb') as f, open(self.concat_list_file, 'a') as f_list:
                f.write(response.content)
                f_list.write(f"file '{self.download_path}/{filename}.ts'\n")
                
    
    # 拉取第二个 m3u8 文件
    def download_m3u8_file_2(self):
        logger.info("开始拉取第二个 m3u8 文件")
        response = requests.get(self.url_m3u8_file_2)
        with open(self.local_m3u8_file_2, 'w') as f:
            f.write(response.text)

    # 解析第二个 m3u8 文件的 url
    def parse_url_m3u8_file_2(self):
        logger.info("开始解析第二个 m3u8 文件的url...")
        with open(self.local_m3u8_file_1, 'r') as f:
            text = f.read()
            pattern_m3u8_2 = r'\d.*?index.m3u8'
            pattern_m3u8_2_result = re.search(pattern_m3u8_2, text)
            self.url_m3u8_file_2 = self.url_m3u8_file_1.replace('index.m3u8', pattern_m3u8_2_result.group(0))
            logger.info(f"解析出第二个 m3u8 文件的url：{self.url_m3u8_file_2}")

    # 下载第一个 m3u8 文件
    def download_m3u8_file_1(self):
        logger.info(f"开始拉取第一个 m3u8 文件的内容...{self.url_m3u8_file_1}")
        response = requests.get(self.url_m3u8_file_1)
        with open(self.local_m3u8_file_1, 'w') as f:
            f.write(response.text)

    # 解析第一个 m3u8 文件的url
    def prase_url_m3u8_file_1(self):
        logger.info('开始解析第一个 m3u8 文件...')
        pattern_m3u8_1 = r'https:.*?/index.m3u8'
        pattern_m3u8_1_result = re.search(pattern_m3u8_1, self.html)
        self.url_m3u8_file_1 = pattern_m3u8_1_result.group(0).replace('\\', '')
        logger.info(f"解析出第一个 m3u8 文件的 url：{self.url_m3u8_file_1}")

import json
import os
import re
import shutil
from time import time
from bs4 import BeautifulSoup
import ffmpeg
from loguru import logger
import requests
from urllib.parse import urlparse, parse_qs

# TODO: 1. 视频分辨率
# TODO: 2. 只下载音频

class BilibiliDownloader():
    def __init__(self):
        self.website = 'Bilibili'
        self.headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.57",
            "referer": "https://space.bilibili.com/1556651916/dynamic?spm_id_from=333.1365.list.card_title.click"
        }
        self.url = None # 视频页面的url
        self.html = None # 视频页面的html
        self.video_name = None # 视频的标题
        self.video_info = None # 视频信息
        self.video_url = None # 视频的url
        self.audio_url = None # 音频的url
        self.bv_id = None # 视频的bv号
        self.path = os.path.dirname(__file__)
        self.workspace = None 
        self.local_html_file = None
        self.video_file = None # 保存视频文件
        self.audio_file = None # 保存音频文件

        self.max_retry = 5
        self.retry_delay = 3

        self.pod_len = -1 # 分p

    def count_pod(self, html):
        soup = BeautifulSoup(html, 'lxml')
        list = soup.select('div.video-pod .video-pod__list.multip.list .video-pod__item')
        print(f'len={len(list)}')
        return len(list)
    
    def download_pod(self, url):
        self.url = url
        self.html = self.get_html(url)
        self.bv_id = self.parse_bv()
        self.video_name = self.parse_video_name(self.html)
        self.init_workspace()
        self.parse_video_info()
        self.get_video()
        self.get_audio()
        self.merge()
        self.clear_workspace()

    def download(self, url):
        self.url = url
        self.html = self.get_html(url)
        pod_index = self.parse_pod_index_in_url(self.url)
        # url中已经自带分p信息，则只下载当前 p
        if pod_index is not None:
            self.download_pod(url)
        else:
            self.pod_len = self.count_pod(self.html)
            # 不分p
            if self.pod_len == 0:
                self.download_pod(url)
            # 分p
            else:
                for pod_index in range(1, self.pod_len+1):
                    self.download_pod(f'{url}?p={pod_index}')

    def parse_bv(self):
        pattern = r'BV\w{10}'
        match = re.search(pattern, self.url)
        if match is not None:
            bv_id = match.group()
            logger.info(f'[{self.website}] 解析出的BV号: {bv_id}')
            return bv_id
        else:
            logger.error(f'[{self.website}] 未能解析到BV号')

    def init_workspace(self):
        self.workspace = os.path.join(self.path, 'downloads', self.video_name)
        if not os.path.exists(self.workspace):
            os.makedirs(self.workspace)
        else:
            logger.warning('工作目录 {self.workspace} 已经存在')
        self.video_file = os.path.join(self.workspace, f'{self.video_name}.video.mp4')
        self.audio_file = os.path.join(self.workspace, f'{self.video_name}.audio.mp3')
    
    def parse_pod_index_in_url(self, url):
        try:
            parsed_url = urlparse(url)
            query_params = parse_qs(parsed_url.query)
            pod_index = query_params.get('p')[0]
            return pod_index
        except Exception as e:
            return None

    def parse_video_name(self, html):
        pattern = r'class="video-info-title-inner".*?<h1.*?>(.*?)</h1>'
        result = re.search(pattern, html)
        if self.pod_len != 0:
            pod_index = self.parse_pod_index_in_url(self.url)
            soup = BeautifulSoup(html, 'lxml')
            pod_name = soup.select_one('div.video-pod__list.multip.list .video-pod__item.active .title-txt').text
        if result is not None:
            return f'{result.group(1)}-p{pod_index}-{pod_name}'
        else:
            logger.warning('解析视频名称失败')

    def get_html(self, url):
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            logger.info(f"[{self.website}] 下载html")
            return response.text
        else:
            logger.error(f"下载html失败. Status Code: {response.status_code}")

    def parse_video_info(self):
        pattern = r'window.__playinfo__=(.*?)</script>'
        result = re.search(pattern, self.html)
        if result is not None:
            info = result.group(1)
            self.video_info = json.loads(info)
            self.video_url = self.video_info['data']['dash']['video'][0]['baseUrl'] 
            self.audio_url = self.video_info['data']['dash']['audio'][0]['baseUrl'] 
            logger.info(f'[{self.website}] 解析出视频下载地址、音频下载地址')
        else:
            logger.error(f"[{self.website}] 解析视频、音频下载地址失败")

    def get_video(self):
        logger.info(f'[{self.video_name}]')
        for attempt in range(self.max_retry):
            try:
                response = requests.get(self.video_url, headers=self.headers)
                with open(self.video_file, 'wb') as f:
                    f.write(response.content)
                logger.info(f'[{self.video_name}] 视频文件下载成功')
                break
            except requests.exceptions.RequestException as e:
                if attempt < self.max_retry - 1:
                    logger.error(f'[{self.video_name}] 视频下载失败, {self.retry_delay}s 后重试...')
                    time.sleep(self.retry_delay)
                else:
                    logger.error(f'[{self.video_name}] 下载达到最大常识次数, 下载失败')
            except IOError as e:
                logger.error(f'[{self.video_name}] 写入文件失败: {e}')
            except Exception as e:
                logger.error(f'[{self.video_name}] 未知错误：{e}')

    def get_audio(self):
        for attemp in range(self.max_retry):
            try:
                response = requests.get(self.audio_url, headers=self.headers)
                with open(self.audio_file, 'wb') as f:
                    f.write(response.content)    
                logger.info(f'[{self.video_name}] 音频文件下载完成')
                break
            except requests.exceptions.RequestException as e:
                if attemp < self.max_retry:
                    logger.error(f'[{self.video_name}] 音频下载失败， {self.retry_delay}s 后重试...')
                    time.sleep(self.retry_delay)
                else:
                    logger.error(f'[{self.video_name}] 音频达到最大常识次数，下载失败')
            except IOError as e:
                logger.error(f'[{self.video_name}] 音频写入文件失败: {e}')
            except Exception as e:
                logger.error(f'[{self.video_name}] 音频未知错误：{e}')

    def merge(self):
        logger.info(f'[{self.website}] 开始合并视频、音频文件...')
        try:
            video_input = ffmpeg.input(self.video_file)
            audio_input = ffmpeg.input(self.audio_file)
            (
                ffmpeg
                    .output(video_input, audio_input, os.path.join(self.workspace, f'{self.video_name}.mp4'))
                    .run()
            )
        except Exception as e:
            logger.error(f'[{self.video_name}] 合并视频、音频文件出错。{e}')

    def clear_workspace(self):
        video_file = os.path.join(self.workspace, f'{self.video_name}.mp4')
        curr_dir = os.path.dirname(video_file)
        parent_dir = os.path.dirname(curr_dir)
        try:
            shutil.move(video_file, parent_dir)
            shutil.rmtree(self.workspace)
        except Exception as e:
            logger.error(f'清理工作区失败: {e}')

if __name__ == '__main__':
    url = 'https://www.bilibili.com/video/BV16A411W7SQ?p=6' # 分p
    # url = 'https://www.bilibili.com/video/BV16A411W7SQ?p=2'
    # url = 'https://www.bilibili.com/video/BV1Ma9tYPEg4' # 不分p
    downloader = BilibiliDownloader()
    downloader.download(url)
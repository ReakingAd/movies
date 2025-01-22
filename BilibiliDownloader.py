import json
import os
import re
import ffmpeg
from loguru import logger
import requests
# TODO：log
# TODO: 视频分辨率

class BilibiliDownloader():
    def __init__(self):
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

    def parse_bv(self):
        pattern = r'BV\w{10}'
        match = re.search(pattern, self.url)
        if match:
            self.bv_id = match.group(0)
            logger.info(f'解析到的BV号：{self.bv_id}')
        else:
            logger.error('未能解析到BV号')
    def init_workspace(self):
        self.workspace = os.path.join(self.path, 'downloads', self.bv_id)
        if not os.path.exists(self.workspace):
            os.makedirs(self.workspace)
            logger.info('创建工作目录成功')
        else:
            logger.warning('工作目录 {self.workspace} 已经存在')
        self.local_html_file = os.path.join(self.workspace, 'index.html')
        with open(self.local_html_file, 'w', encoding="utf-8") as f:
            f.write(self.html)
        self.video_file = os.path.join(self.workspace, f'{self.bv_id}.video.mp4')
        self.audio_file = os.path.join(self.workspace, f'{self.bv_id}.audio.mp3')
    
    def parse_video_name(self):
        pattern = r'class="video-info-title-inner".*?<h1.*?>(.*?)</h1>'
        result = re.search(pattern, self.html)
        if result is not None:
            self.video_name = result.group(1)
        else:
            logger.warning('解析视频名称失败')
    def download(self, url):
        self.url = url
        self.get_html()
        self.parse_bv()
        self.parse_video_name()
        self.init_workspace()
        self.parse_video_info()
        self.get_video()
        self.get_audio()
        self.merge()

    def get_html(self):
        logger.info("开始下载html...")
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            logger.info("下载html成功")
            self.html = response.text
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
            logger.info(f'解析playinfo完成,video_url={self.video_url}, audio_url={self.audio_url}')

        else:
            logger.error("解析playinfo失败")

    def get_video(self):
        response = requests.get(self.video_url, headers=self.headers)
        if response.status_code == 200:
            with open(self.video_file, 'wb') as f:
                f.write(response.content)
            logger.info('下载视频文件成功')
        else:
            logger.error("下载视频失败")

    def get_audio(self):
        response = requests.get(self.audio_url, headers=self.headers)
        if response.status_code == 200:
            with open(self.audio_file, 'wb') as f:
                f.write(response.content)
            logger.info('下载音频文件成功')
        else:
            logger.error("下载音频失败")
    def merge(self):
        logger.info("开始合并视频和音频...")
        video_input = ffmpeg.input(self.video_file)
        audio_input = ffmpeg.input(self.audio_file)
        ffmpeg.output(video_input, audio_input, os.path.join(self.workspace, f'{self.video_name}.mp4')).run()
        logger.info('视频视频完成。')



if __name__ == '__main__':
    url = 'https://www.bilibili.com/video/BV1Z3wsebEKk'
    downloader = BilibiliDownloader()
    downloader.download(url)
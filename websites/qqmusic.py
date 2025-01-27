import json
import os
import re
import ffmpeg
from loguru import logger
from playwright.sync_api import sync_playwright, expect, TimeoutError as PlaywrightTimeoutError
import requests
"""
使用 playwright 模拟真人用户操作
1. 如果首次使用，或者登陆过期，要先执行 downloader.auth(url) 扫码登陆。
2. 执行 downloader.download(url)

TODO: 1. headless模式下的bug：play page第一个music.fcg返回的数据就不对，导致没有发起第二个music.fcg请求
TODO: 2. 文件后缀 m4a 是不得解析得来。以防有些歌曲不是m4a格式？

"""

class QQMusicDownloader():
    def __init__(self):
        self.path = os.path.dirname(__file__)
        self.url = None
        self.state_dir = os.path.join(self.path, 'states')
        self.state_file = os.path.join(self.state_dir, 'qqmusic.json')
        self.download_dir = os.path.join(self.path, 'downloads')

        self.has_play_page = False # 是否已经打开了播放页
        self.request_count = 0 # 播放页 musics.fcg 接口调用的计数 

        self.music_download_url = None # 歌曲下载地址
        self.music_name = None # 歌曲名称
        self.music_name_with_ext = None # 歌曲名称(带后缀名)

    def auth(self, url):
        print(url)
        self.url = url
        with sync_playwright() as playwright:
            edge_path = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe"
            browser = playwright.chromium.launch(headless=False, executable_path=edge_path)
            context = browser.new_context()
            page = context.new_page() # 在context中创建新页面
            page.goto(url)
            expect(page.locator('img.top_login__cover')).to_be_visible(timeout=10*60*1000)
            if not os.path.exists(self.state_dir):
                os.makedirs(self.state_dir)
            context.storage_state(path=self.state_file)
            input("Press Enter to close the browser...")

    def convert_m4a_to_mp3(self, input_file, output_file):
        try:
            print(f'[QQMusic] Convert {self.music_name}.m4a to {self.music_name}.mp3')
            (
                ffmpeg
                .input(input_file)
                .output(output_file)
                .global_args('-loglevel', 'error')  # 设置日志级别为 'error'
                .global_args('-y')
                .global_args('-stats')
                .run()
            )

        except ffmpeg.Error as e:
            logger.error(f"{e.stderr.decode()}")

    def get_music(self, url):
        print(f'[QQMusic] Downloading music from {url}')
        resp = requests.get(url)
        if resp.status_code == 200:
            if not os.path.exists(self.download_dir):
                os.makedirs(self.download_dir)
            with open(os.path.join(self.download_dir, self.music_name_with_ext), 'wb') as f:
                f.write(resp.content)
                
        else:
            logger.debug(resp.status_code)

    def delete_origin_file(self):
        try:
            print(f'[QQMusic] Deleting original file {self.music_name_with_ext}')
            os.remove(os.path.join(self.download_dir, self.music_name_with_ext))
        except OSError as e:
            logger.error(f"Error: {e.strerror}")
    def handle_lanjie(self, route, req):
        """
        链接器处理函数
        page[0] 是 歌曲详情页
        page[1] 是 歌曲播放页
        播放页的第二个music.fcg接口歌曲的信息数据
        
        """
        if self.has_play_page == False: # False,说明 play page 还没有。所以直接继续
            route.continue_()
            return
        self.request_count += 1
        if self.request_count == 2:
            print(f'[QQMusic] Requesting "music.fcg" for music info')
            response = requests.post(req.url, headers=req.headers, data=req.post_data)
            if response.status_code == 200:
                json_data = json.loads(response.text)
                self.music_download_url = f'https://ws6.stream.qqmusic.qq.com/{json_data['req_6']['data']['midurlinfo'][0]['purl']}'
                self.music_name_with_ext = f"{json_data['req_1']['data']['tracks'][0]['title']}.m4a"
                self.get_music(self.music_download_url)
                self.convert_m4a_to_mp3(os.path.join(self.download_dir, self.music_name_with_ext), os.path.join(self.download_dir, f'{self.music_name}.mp3'))
                self.delete_origin_file()
            else:
                print(response.status_code)
        route.continue_()

    def download(self, url):
        print(f'[QQMusic] Extracting URL: {url}')
        with sync_playwright() as playwright:
            edge_path = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe"
            browser = playwright.chromium.launch(headless=False, executable_path=edge_path)
            context = browser.new_context(storage_state=self.state_file)
            context.route(re.compile(r'http.*?musics\.fcg.*?$'), self.handle_lanjie) # 监听所有pages中所有musics.fcg接口的请求

            detail_page = context.new_page() # 歌曲详情页
            detail_page.goto(url, wait_until='load', timeout=60000)
            expect(detail_page.locator('div[role="toolbar"].data__actions a.mod_btn_green')).to_be_visible()
            self.music_name = detail_page.locator('h1.data__name_txt').inner_text()

            print(f'[QQMusic] opening play page')
            self.has_play_page = True # 点击播放按钮前(也就是播放页生成前)，将标志位置为True。目的是标记不用处理详情页的musics.fcg接口
            detail_page.locator('div[role="toolbar"].data__actions a.mod_btn_green').click() # 点击详情页的播放按钮
            detail_page.wait_for_timeout(1000) # **加了context.route()拦截后，必须得有这一行，才能在play page(播放页)看到要播放的歌曲。不知道为什么**
            context.pages[1].wait_for_timeout(1000) # **加了context.route()拦截后，必须得有这一行。否则在按回车结束input()后，会报错。不知道为什么**
            
            input('Press Enter to Exit......')

if __name__ == '__main__':
    url = 'https://y.qq.com/n/ryqq/songDetail/0015BszJ09xZ2z'
    downloader = QQMusicDownloader()
    # downloader.auth(url)
    downloader.download(url)
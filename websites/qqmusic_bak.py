import json
import os
import re
import time
import ffmpeg
from loguru import logger
from playwright.sync_api import sync_playwright, expect, TimeoutError as PlaywrightTimeoutError
import requests
"""
使用 playwright 模拟用户操作

"""
# TODO： context.on('requets')是不是有bug，相同的两个请求，不同的参数，只能监听到第一个请求
class QQMusicDownloader():
    def __init__(self):
        self.path = os.path.dirname(__file__)
        self.url = None
        self.state_dir = os.path.join(self.path, 'state')
        self.state_file = os.path.join(self.state_dir, 'qqmusic.json')
        self.download_dir = os.path.join(self.path, 'downloads')
        # self.download_file = os.path.join(self.download_dir, 'xxxx.mp3')

    def auth(self, url):
        logger.info(url)
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
            ffmpeg.input(input_file).output(output_file).run()
        except ffmpeg.Error as e:
            logger.error(f"{e.stderr.decode()}")
    def download(self, url):
        with sync_playwright() as playwright:
            edge_path = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe"
            browser = playwright.chromium.launch(headless=False, executable_path=edge_path)
            context = browser.new_context(storage_state=self.state_file)
            has_play_page = False # 是否已经打开了播放页
            request_count = 0 # 播放页 musics.fcg 接口调用的计数 
            def handle_lanjie(route, req):
                nonlocal request_count
                nonlocal has_play_page
                if has_play_page == False: # False,说明 play page 还没有。所以直接继续
                    route.continue_()
                    return
                request_count += 1
                if request_count == 2:
                    response = requests.post(req.url, headers=req.headers, data=req.post_data)
                    if response.status_code == 200:
                        json_data = json.loads(response.text)
                        music_download_url = f'https://ws6.stream.qqmusic.qq.com/{json_data['req_6']['data']['midurlinfo'][0]['purl']}'
                        # TODO: m4a文件后缀是不得解析得来。以防有些歌曲不是m4a格式？
                        music_name = f"{json_data['req_1']['data']['tracks'][0]['title']}"
                        music_name_ext = f"{json_data['req_1']['data']['tracks'][0]['title']}.m4a"
                        resp = requests.get(music_download_url)
                        if resp.status_code == 200:
                            if not os.path.exists(self.download_dir):
                                os.makedirs(self.download_dir)
                            with open(os.path.join(self.download_dir, music_name_ext), 'wb') as f:
                                f.write(resp.content)
                                self.convert_m4a_to_mp3(os.path.join(self.download_dir, music_name_ext), os.path.join(self.download_dir, f'{music_name}.mp3'))
                        else:
                            logger.debug(resp.status_code)
                    else:
                        print(response.status_code)
                route.continue_()

            context.route(re.compile(r'http.*?musics\.fcg.*?$'), handle_lanjie) # 监听所有pages中所有musics.fcg接口的请求
            detail_page = context.new_page() # 歌曲详情页
            detail_page.goto(url, wait_until='load', timeout=60000)
            expect(detail_page.locator('div[role="toolbar"].data__actions a.mod_btn_green')).to_be_visible()
            has_play_page = True # 点击播放按钮前(也就是播放页生成前)，将标志位置为True。目的是标记不用处理详情页的musics.fcg接口
            detail_page.locator('div[role="toolbar"].data__actions a.mod_btn_green').click() # 点击详情页的播放按钮
            detail_page.wait_for_timeout(1000) # **加了context.route()拦截后，必须得有这一行，才能在play page(播放页)看到要播放的歌曲。不知道为什么**
            context.pages[1].wait_for_timeout(1000) # **加了context.route()拦截后，必须得有这一行。否则在按回车结束input()后，会报错。不知道为什么**
            input('按回车退出......')
    def download_bak(self, url):
        with sync_playwright() as playwright:
            edge_path = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe"
            browser = playwright.chromium.launch(headless=False, executable_path=edge_path)
            context = browser.new_context(storage_state='state.json', record_video_dir='record.mp4')
            context.tracing.start(screenshots=True,snapshots=True,sources=True)
            flag = False
            count = 0
            # 禁用缓存
            # context.set_default_navigation_timeout(60000)
            # context.set_default_timeout(60000)
            def lanjie(route, request):
                nonlocal flag
                if flag == False: # False,说明 play page 还没有。所以直接继续
                    route.continue_()
                    return
                nonlocal count
                count += 1
                if count == 2:
                    logger.info(request.url)
                    response = requests.post(request.url, headers=request.headers, data=request.post_data)
                    if response.status_code == 200:
                        # print(response.text)
                        json_data = json.loads(response.text)
                        music_url = f'https://ws6.stream.qqmusic.qq.com/{json_data['req_6']['data']['midurlinfo'][0]['purl']}'
                        logger.debug(music_url)
                        resp = requests.get(music_url)
                        if resp.status_code == 200:
                            with open('111111.mp3', 'wb') as f:
                                f.write(resp.content)
                        else:
                            logger.debug(resp.status_code)
                    else:
                        print(response.status_code)
                route.continue_()

            # context.route(r'^http.*?musics.fcg.*?$', lanjie)
            context.route(re.compile(r'^http.*?musics\.fcg.*?$'), lanjie)

            detail_page = context.new_page() # 歌曲详情页：在context中创建新页面
            detail_page.goto(url, wait_until='load', timeout=60000) # 打开详情页，不使用缓存
            detail_page.wait_for_timeout(2000)
            flag = True
            detail_page.locator('div[role="toolbar"].data__actions a.mod_btn_green').click() # 点击“播放”按钮
            detail_page.wait_for_timeout(2000)
            expect(context.pages[1].locator('a.btn_big_play')).to_be_visible()

            print(context.pages[0].title())
            print(context.pages[1].title())
            play_page = context.pages[1]
            """
            play_page.reload() ##### 重新刷新播放页面这句是精髓。
            不然由于点击“播放”按钮后，马上就打开了新页面。很有可能导致on('request')监听不到早发出的请求
            """
            # play_page.reload(wait_until='load', timeout=60000)
            # context.pages[0].bring_to_front()
            input("Press Enter....................")

if __name__ == '__main__':
    url = "https://y.qq.com/n/ryqq/songDetail/0047a9I84FGka6"
    # url = 'https://y.qq.com/n/ryqq/songDetail/002QcvUW3FUmyr'
    downloader = QQMusicDownloader()
    # downloader.auth(url)
    downloader.download(url)
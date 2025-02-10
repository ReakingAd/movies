import json
import os
import re
import time
import ffmpeg
from loguru import logger
from playwright.sync_api import sync_playwright, expect, TimeoutError as PlaywrightTimeoutError
import requests
"""
使用 playwright 模拟真人用户操作
1. 如果首次使用，或者登陆过期，要先执行 downloader.auth(url) 扫码登陆。
2. 执行 downloader.download(url)

TODO: 0. 进入play页面，先hover，出现播放按钮后点击播放，看会不会出现第二次接口
TODO: 1. headless模式下的bug：play page第一个music.fcg返回的数据就不对，导致没有发起第二个music.fcg请求
TODO: 2. 下载歌单
    - 歌单列表  post  https://u6.y.qq.com/cgi-bin/musics.fcg?_=1738385137683&sign=zzc866b382epzcrf0uzij5ibttmujmhszzfq3bf82561
    - 负载： req_3":{"module":"music.srfDissInfo.aiDissInfo","method":"uniform_get_Dissinfo","param":{"disstid":8353804440,"userinfo":1,"tag":1,"orderlist":1,"song_begin":0,"song_num":10,"onlysonglist":0,"enc_host_uin":""}},"
    关键点 song_begin, song_num
TODO: 3. task.py 不能正常退出主进程。join()理解的不够，学学
"""

class QQMusicDownloader():
    def __init__(self):
        self.download_gap = 2 # 每次下载歌曲时，先等带几秒。避免爬取太频繁被封禁
        self.detail_page = None # 详情页
        self.album_url = None # 专辑详情页
        self.gen_song_id_list = None # 专辑的播放列表
        self.max_retry = 5 # 下载最大常识次数
        self.retry_delay = 5 # 下载重试前设置的延迟


        self.path = os.path.dirname(__file__)
        self.url = None
        self.state_dir = os.path.join(self.path, 'states')
        self.state_file = os.path.join(self.state_dir, 'qqmusic.json')
        self.download_dir = os.path.join(self.path, 'downloads')
        # self.album_dir = os.path.join(self.download_dir)
        self.album_dir = None

        self.has_play_page = False # 是否已经打开了播放页
        self.request_count = 0 # 播放页 musics.fcg 接口调用的计数 

        self.music_download_url = None # 歌曲下载地址
        self.music_name = None # 歌曲名称
        self.music_name_with_ext = None # 歌曲名称(带后缀名)

    def auth(self, song_id):
        print(song_id)
        self.url = f'https://y.qq.com/n/ryqq/songDetail/{song_id}'
        with sync_playwright() as playwright:
            edge_path = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe"
            browser = playwright.chromium.launch(headless=False, executable_path=edge_path)
            context = browser.new_context()
            page = context.new_page() # 在context中创建新页面
            page.goto(self.url)
            expect(page.locator('img.top_login__cover')).to_be_visible(timeout=10*60*1000)
            if not os.path.exists(self.state_dir):
                os.makedirs(self.state_dir)
            context.storage_state(path=self.state_file)
            input("Press Enter to close the browser...")

    def convert_m4a_to_mp3(self, input_file, output_file):
        try:
            print(f'[QQMusic] 将 {self.music_name}.m4a 转换为 {self.music_name}.mp3')
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
        print(f'[QQMusic] 等待 {self.download_gap} 秒..... 后开始下载 {url}')
        time.sleep(self.download_gap)  # 添加时间间隔，避免请求过快
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
            print(f'[QQMusic] 删除源文件 {self.music_name_with_ext}')
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
        route.continue_()
        if self.has_play_page == False: # False,说明 play page 还没有。所以直接继续
            # route.continue_()
            return
        self.request_count += 1
        if self.request_count == 2:
            self.has_play_page = False
            self.request_count = 0
            response = requests.post(req.url, headers=req.headers, data=req.post_data)
            if response.status_code == 200:
                json_data = json.loads(response.text)
                purl = json_data['req_6']['data']['midurlinfo'][0]['purl']
                self.music_download_url = f'https://ws6.stream.qqmusic.qq.com/{purl}'
                self.music_name_with_ext = f"{json_data['req_1']['data']['tracks'][0]['title']}.m4a"
                self.get_music(self.music_download_url)
                self.convert_m4a_to_mp3(os.path.join(self.download_dir, self.music_name_with_ext), os.path.join(self.download_dir, f'{self.music_name}.mp3'))
                self.delete_origin_file()
            else:
                print(response.status_code)
        # route.continue_()

    def download_song(self, song_id):
        self.url = f'https://y.qq.com/n/ryqq/songDetail/{song_id}'
        print(f'[QQMusic] 拉取 URL: {self.url}')
        for i in range(3):
            try:
                with sync_playwright() as playwright:
                    edge_path = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe"
                    browser = playwright.chromium.launch(headless=False, executable_path=edge_path)
                    context = browser.new_context(storage_state=self.state_file)
                    context.route(re.compile(r'http.*?musics\.fcg.*?$'), self.handle_lanjie) # 监听所有pages中所有musics.fcg接口的请求

                    detail_page = context.new_page() # 歌曲详情页
                    detail_page.goto(self.url, wait_until='load', timeout=60000)
                    expect(detail_page.locator('div[role="toolbar"].data__actions a.mod_btn_green')).to_be_visible()
                    self.music_name = detail_page.locator('h1.data__name_txt').inner_text()

                    self.has_play_page = True # 点击播放按钮前(也就是播放页生成前)，将标志位置为True。目的是标记不用处理详情页的musics.fcg接口
                    detail_page.locator('div[role="toolbar"].data__actions a.mod_btn_green').click() # 点击详情页的播放按钮
                    detail_page.wait_for_timeout(1000) # **加了context.route()拦截后，必须得有这一行，才能在play page(播放页)看到要播放的歌曲。不知道为什么**
                    context.pages[1].wait_for_timeout(1000) # **加了context.route()拦截后，必须得有这一行。否则在按回车结束input()后，会报错。不知道为什么**
                    break # 执行到此不报错，说明当前歌曲下载成功。跳出重试机制
            except Exception as e:
                print(f'[QQMusic] {song_id}:下载发生错误：{e}')
                if i < self.max_retry-1:
                    print(f"等待 {self.retry_delay} 秒后重试...")
                    time.sleep(self.retry_delay)
                else:
                    print(f"{song_id}:已经达到最大尝试次数")

    def handle_album_lanjie(self, route, req):
        route.continue_()
        resp = requests.request(req.method, req.url, headers=req.headers, data=req.post_data)
        if resp.status_code == 200:
            json_data = json.loads(resp.text)
            album_name = json_data['data']['album_name']
            singername = json_data['data']['singerinfo'][0]['singername']
            companyname = json_data['data']['companyname']
            publictime = json_data['data']['publictime']
            desc = json_data['data']['desc']
            self.download_dir = os.path.join(self.download_dir, f'{album_name}@{singername}')
            self.gen_song_id_list = (song['songmid'] for song in json_data['data']['songlist'])
            gen_song_name_list = [song['songname'] for song in json_data['data']['songlist']]
            if not os.path.exists(self.download_dir):
                os.makedirs(self.download_dir)
                with open(os.path.join(self.download_dir, 'album_info.txt'), 'w', encoding="utf-8") as f:
                    f.write(f'专辑: {album_name}\n')
                    f.write(f'歌手: {singername}\n')
                    f.write(f'发行时间: {publictime}\n')
                    f.write(f'唱片公司: {companyname}\n')
                    f.write(f'简介: {desc}\n')
                    f.write(f'歌曲列表: \n')
                    for index, song_name in  enumerate(gen_song_name_list):
                        f.write(f'{index+1}. {song_name}\n')
        else:
            print(f'[QQMusic] 获取歌曲列表失败')

    def download_album(self, album_id):
        self.album_url = f'https://y.qq.com/n/ryqq/albumDetail/{album_id}'
        print(f'[QQMusic] 拉取 URL: {self.album_url}')
        with sync_playwright() as playwright:
            edge_path = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe"
            browser = playwright.chromium.launch(headless=False, executable_path=edge_path)
            context = browser.new_context(storage_state=self.state_file)
            context = context
            context.route(re.compile(r'http.*?musicmall\.fcg.*?$'), self.handle_album_lanjie)
            detail_page = context.new_page()
            detail_page.goto(self.album_url, wait_until='load', timeout=60*1000)
            # input('Press Enter to Exit...')
        for song_id in self.gen_song_id_list:
            self.download_song(song_id)
        # input('Press Enter to Exit...')

if __name__ == '__main__':
    url = 'https://y.qq.com/n/ryqq/songDetail/0015BszJ09xZ2z'
    
    downloader = QQMusicDownloader()

    song_id = '0015BszJ09xZ2z'
    downloader.auth(song_id)
    # downloader.download_song(song_id)
    
    # album_id = '002q7zOx4DkZBr'
    # downloader.download_album(album_id)
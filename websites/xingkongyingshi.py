import re
from loguru import logger
# from websites.downloader_base import DownloaderBase
from downloader_base import DownloaderBase

# 星空影视
class XingKongYingShiDownloader(DownloaderBase):
    def __init__(self):
        self.website = '星空影视'
    def parse_film_name(self):
        pattern = r'hl-infos-title">.*?<a.*?>(.*?)</a>.*?<em.*?>(.*?)</em>'
        result = re.search(pattern, self.html)
        
        if result is not None:
            self.film_name = f'{result.group(1)}{result.group(2)}'.replace('&nbsp;', '')
        else:
            logger.error(f'解析电影名错误..') 
    def parse_urls_video_segment(self):
        pattern_url = r'#EXTINF:.*?,\s(.*?\.ts)'
        with open(self.local_m3u8_file_2, 'r') as f:
            content = f.read()
            matches = re.finditer(pattern_url, content)
            self.urls = [re.sub(r'(index|mixed).m3u8', match.group(1), self.url_m3u8_file_2) for match in matches]
            # self.urls_len = 2083
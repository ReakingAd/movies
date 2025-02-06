import re
from loguru import logger
from downloader_base import DownloaderBase

# 茶杯狐影院
class ChaBeiHuDownloader(DownloaderBase):
    def parse_film_name(self):
        pattern_filmname = r'<h1 class="title".*?<span >(.*?)</span>(.*?)</a>'
        result = re.search(pattern_filmname, self.html)
        if result is not None:
            self.film_name = f'{result.group(1)}{result.group(2)}'
        else:
            logger.error(f'解析电影名错误..')
    
    def parse_urls_video_segment(self):
        pattern_url = r'https://.*?\.jpeg'
        with open(self.local_m3u8_file_2, 'r') as f:
            content = f.read()
            matches = re.finditer(pattern_url, content)
            self.urls = (match.group(0) for match in matches)  
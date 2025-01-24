import re

from loguru import logger
from websites.bilibiil import BilibiliDownloader
from websites.chabeihu import ChaBeiHuDownloader
from websites.douyin import DouyinDownloader
from websites.xingkongyingshi import XingKongYingShiDownloader
# TODO：下载cookie到cookies.txt，使用 Netscape format
# 工厂模式：
class Website_Handler_Factory():
    @staticmethod
    def create_handler(site_name):
        if site_name == 'xingkongyingshi':
            return XingKongYingShiDownloader()
        elif site_name == 'chabeihu':
            return ChaBeiHuDownloader()
        elif site_name == 'bilibili':
            return BilibiliDownloader()
        elif site_name == 'douyin':
            return DouyinDownloader()
        else:
            raise ValueError(f'未知的站点：{site_name}')

        
if __name__ == '__main__':
    # handler = Website_Handler_Factory.create_handler('chabeihu')
    # handler.download('https://www.chabei1.com/vodplay/87783-1-1.html')

    # handler = Website_Handler_Factory.create_handler('xingkongyingshi')
    # handler.download('https://www.xkvvv.com/play/6874/1/1/')

    # url = 'https://www.bilibili.com/video/BV1Z3wsebEKk'
    # handler = Website_Handler_Factory.create_handler('bilibili')
    # handler.download(url)

    # url = 'https://www.douyin.com/user/MS4wLjABAAAAkiq8LIkcpNLZO-oRIVLYiAT7cy6Fqf8rc_gRfyb-cNs?from_tab_name=main&modal_id=7427263655978323235'
    url = 'https://www.douyin.com/user/MS4wLjABAAAAuefGYlA8R1LkM9_sdOA_bjLeRgdWw1Kq9dAlQgRP-bEt90e3XJsf1cBKrgOcnskS?from_tab_name=main&modal_id=7440318809648418084'
    handler = Website_Handler_Factory.create_handler('douyin')
    handler.download(url)
    
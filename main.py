from abc import ABC, abstractmethod
import os
import re
import time

import ffmpeg
from loguru import logger
import requests

from websites import Website_ChaBeiHu, Website_XingKongYingShi

# TODO: 2. 删除多余的碎片文件

# 工厂模式：
class Website_Handler_Factory():
    @staticmethod
    def create_handler(site_name):
        if site_name == 'xingkongyingshi':
            return Website_XingKongYingShi()
        elif site_name == 'chabeihu':
            return Website_ChaBeiHu()
        else:
            raise ValueError(f'未知的站点：{site_name}')
        
if __name__ == '__main__':
    # handler = Website_Handler_Factory.create_handler('chabeihu')
    # handler.download('https://www.chabei1.com/vodplay/87783-1-1.html')

    handler = Website_Handler_Factory.create_handler('xingkongyingshi')
    handler.download('https://www.xkvvv.com/play/6874/1/1/')
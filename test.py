from enum import Enum
import re

import requests

class Color(Enum):
    RED = 1
    GREEN = 2

if __name__ == '__main__':
    # for color in Color: print(color)
    # print(Color.GREEN == Color.GREEN)
    # print(Color.GREEN is Color.GREEN)
    # url = 'https://encrypt-k-vod.xet.tech/529d8d60vodtransbj1252524126/d0234f991397757899218552840/drm/v.f421220.m3u8?sign=36a1da8ac2b074e9556e40e756f8a4fb&t=67a580eb&us=jCKOJDsxjF'
    # pattern = r'http.*?\.m3u8\S+'
    # result = re.fullmatch(pattern, url)
    # print(result.group())
    url = 'https://bdcdncmn2.inter.71edge.com/videos/vts/20250206/b6/82/b59999c2296d3a04212beff74482b1e1.ts?key=0aaa66747d91a3ed337056ea053845d77&dis_k=816edf357f4e19e33a716f8f3ae9e4c9&dis_t=1738901879&dis_dz=CMNET-NeiMeng&dis_st=141&src=iqiyi.com&dis_hit=0&dis_tag=01010000&uuid=279b0122-67a58977-2ee&qd_uid=0&qd_k=4853a84af7d656b08453fa2d4e1efd8e&qd_vipres=0&mss=1&fr=25&qd_src=01010031010000000000&pv=0.1&start=6644736&cpt=0&cross-domain=1&qyid=7abb69afa7a2fc8f97c0f7e49fa49634&bid=500&qd_sc=ad44b0d702ca50c96b1ccd80a02a7757&contentlength=6291456&qd_tm=1738901621872&qd_p=279b0122&qd_tvid=3794745815668900&cid=2&ssl=1&qd_index=vod&qd_vip=0&sd=370000&stauto=1&end=12936192&vcodec=2&cphc=arta&ori=pcw1&num=1738901912009'
    resp = requests.get(url)
    if resp.status_code == 200:
        # print(resp.text)
        with open('1111.ts', 'wb') as f:
            f.write(resp.content)
    else:
        print(resp.status_code)
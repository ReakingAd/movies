from abc import ABC, abstractmethod
import re
from urllib.error import URLError
from urllib.request import ProxyHandler, build_opener

import requests
import json
import gzip
import sys
import ffmpeg


def get_page(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Cookie': 'your_cookie_here'
    }
    response = requests.get(url, headers=headers)
    # response = requests.get(url)
    response.encoding = response.apparent_encoding
    return response.text

def test():
    url = 'https://www.bilibili.com/video/BV1MxwpeGEQY'
    # print(url)
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'referer': 'https://www.bilibili.com/video/BV15j421U7a5/?spm_id_from=333.337.search-card.all.click&vd_source=fda0d59c12dcd36c1eccec649fa28042',
        'Cookie': "your_updated_cookie_here",
        # ':authority': 'data.bilibili.com',
        # ':method': 'GET',
        # ":path": "/upgcxcode/89/11/1458141189/1458141189-1-100048.m4s?e=ig8euxZM2rNcNbdlhoNvNC8BqJIzNbfqXBvEqxTEto8BTrNvN0GvT90W5JZMkX_YN0MvXg8gNEV4NC8xNEV4N03eN0B5tZlqNxTEto8BTrNvNeZVuJ10Kj_g2UB02J0mN0B5tZlqNCNEto8BTrNvNC7MTX502C8f2jmMQJ6mqF2fka1mqx6gqj0eN0B599M=&uipk=5&nbs=1&deadline=1737382078&gen=playurlv2&os=08cbv&oi=664469761&trid=c145ce99ddcb4b1eb0e2b3959e0aacf4u&mid=3546600053934402&platform=pc&og=hw&upsig=632734720b2106c472b2a04e182ade8b&uparams=e,uipk,nbs,deadline,gen,os,oi,trid,mid,platform,og&bvc=vod&nettype=0&orderid=0,3&buvid=62E1069C-98FB-9C72-B3E7-7D06965B888094762infoc&build=0&f=u_0_0&agrr=0&bw=142749&logo=80000000",
        # ':scheme': 'https'
        'accept': '*/*',
        'accept-encoding': 'identity',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'if-range': '316be20ee04467267648192042fb2586',
        'origin': 'https://www.bilibili.com',
        'range': 'bytes=9142940-9849707',
        'referer': 'https://www.bilibili.com/video/BV15j421U7a5/?spm_id_from=333.337.search-card.all.click&vd_source=fda0d59c12dcd36c1eccec649fa28042',
        'sec-ch-ua': '"Microsoft Edge";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site'
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            print(response.text)
            with open('test.m4s', 'wb') as f:
                f.write(response.content)
        else:
            print(f'Status Code: {response.status_code}')
            print(f'Headers: {response.headers}')
            print(f'Content: {response.content}')
            with open('test.m4s', 'wb') as f:
                f.write(response.content)
    except requests.exceptions.RequestException as e:
        print('Failed to download video')
        print(f'Error: {e}')
    # if response.status_code == 200:
    #     print(response.text)
    # else:
    #     print(response.status_code)
def test2():
    arr = [
        {'a1': 1, 'b2': 2},
        {'a2': 1, 'b2': 2},
    ]
    for key in arr:
        print(key)

if __name__ == '__main__':
    # url = 'https://www.bilibili.com/video/BV15j421U7a5/'
    url = 'https://www.bilibili.com/video/BV1xCw6eXE1n/'
    # test2()
    # sys.exit()
    html = get_page(url=url)
    pattern = r'window.__playinfo__=(.*?)</script>'
    result = re.search(pattern, html)
    json_data = json.loads(result.group(1))
    print(json_data['code'])
    formatted_json = json.dumps(json_data, indent=4, ensure_ascii=False)

    # index = 1
    # for key in json_data['data']['dash']['video']:
    #     # print(key.baseUrl)
    #     print(key.get('baseUrl'))
    #     video_url = key.get('baseUrl')

    video_url = json_data['data']['dash']['video'][0]['baseUrl']
    audio_url = json_data['data']['dash']['audio'][0]['baseUrl']
    # print(video_url)
    # print(audio_url)
        # sys.exit()
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
            'referer': 'https://www.bilibili.com/video/BV15j421U7a5/?spm_id_from=333.337.search-card.all.click&vd_source=fda0d59c12dcd36c1eccec649fa28042',
        }
        response = requests.get(video_url, headers=headers)
        print(response.status_code)
        with open(f'video.mp4', 'wb') as f:
            f.write(response.content)
            # index += 1
    except requests.exceptions.RequestException as e:
        print('Failed to download video')
        print(f'Error: {e}')
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
            'referer': 'https://www.bilibili.com/video/BV15j421U7a5/?spm_id_from=333.337.search-card.all.click&vd_source=fda0d59c12dcd36c1eccec649fa28042',
        }
        response = requests.get(audio_url, headers=headers)
        print(response.status_code)
        with open('video.mp3', 'wb') as f:
            f.write(response.content)
        # Merge video and audio using ffmpeg
        input_video = ffmpeg.input('video.mp4')
        input_audio = ffmpeg.input('video.mp3')
        ffmpeg.output(input_video, input_audio, 'output2.mp4').run()
    except requests.exceptions.RequestException as e:
        print('Failed to download video')
        print(f'Error: {e}')
    # print(json_data)

    # https://upos-sz-estghw.bilivideo.com/upgcxcode/89/11/1458141189/1458141189-1-30232.m4s?e=ig8euxZM2rNcNbdlhoNvNC8BqJIzNbfqXBvEqxTEto8BTrNvN0GvT90W5JZMkX_YN0MvXg8gNEV4NC8xNEV4N03eN0B5tZlqNxTEto8BTrNvNeZVuJ10Kj_g2UB02J0mN0B5tZlqNCNEto8BTrNvNC7MTX502C8f2jmMQJ6mqF2fka1mqx6gqj0eN0B599M=&uipk=5&nbs=1&deadline=1737371585&gen=playurlv2&os=upos&oi=664469761&trid=77e66276c59c4a7d8ce7a939b11fa180u&mid=3546600053934402&platform=pc&og=hw&upsig=625d369cdf1339a91b5ed6a488124636&uparams=e,uipk,nbs,deadline,gen,os,oi,trid,mid,platform,og&bvc=vod&nettype=0&orderid=0,3&buvid=62E1069C-98FB-9C72-B3E7-7D06965B888094762infoc&build=0&f=u_0_0&agrr=1&bw=12670&logo=80000000
    # https://upos-sz-mirrorcos.bilivideo.com/upgcxcode/89/11/1458141189/1458141189-1-100110.m4s?e=ig8euxZM2rNcNbdlhoNvNC8BqJIzNbfqXBvEqxTEto8BTrNvN0GvT90W5JZMkX_YN0MvXg8gNEV4NC8xNEV4N03eN0B5tZlqNxTEto8BTrNvNeZVuJ10Kj_g2UB02J0mN0B5tZlqNCNEto8BTrNvNC7MTX502C8f2jmMQJ6mqF2fka1mqx6gqj0eN0B599M=&uipk=5&nbs=1&deadline=1737376207&gen=playurlv2&os=cosbv&oi=664469761&trid=dda8dd5c62f44d4cbd16bff075f57b58u&mid=0&platform=pc&og=cos&upsig=3f60f6f27b699013186bca7cdbc1c541&uparams=e,uipk,nbs,deadline,gen,os,oi,trid,mid,platform,og&bvc=vod&nettype=0&orderid=0,3&buvid=&build=0&f=u_0_0&agrr=1&bw=43237&logo=80000000
import json
import os
import pprint
import re
from loguru import logger
import requests
import urllib.parse

class DouyinDownloader():
    def __init__(self):
        self.path = os.path.dirname(__file__)
        self.workspace = None
        self.url = None
        self.headers = {}
        
        self.html = None
        self.video_url = None # 视频下载地址
        self.author = None # 视频作者
        self.video_name = None # 视频名称
    def init_workspace(self):
        self.workspace = os.path.join(self.path, 'downloads', self.video_name)
        if not os.path.exists(self.workspace):
            os.makedirs(self.workspace)
            logger.info(f'创建工作目录完成：{self.workspace}')
        else:
            logger.info(f'影片工作目录已经存在：{self.workspace}')

    def download(self, url):
        self.url = url
        self.headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.57",
            "referer": url,
            "cookie": "ttwid=1%7Cp5JPW5IrqzNTVLM9BollkEeEUXkgQxP9YpRDQqCl-AY%7C1737562941%7Cc6d089ab807d8d4b60d811ea0772fb1e7aa7cae1c51d3dd7742acce2f5828eb9; UIFID_TEMP=481cde0aefb5fd66a02e3857c765c11a58536e172336c332084172243d11b41a237f4618661d280f2fead8bd44cf16d02930961735c6f4660e0660d3a760273fa69c4f7acec3a1527f8097a8800ca513; dy_swidth=1920; dy_sheight=1080; strategyABtestKey=%221737562944.047%22; s_v_web_id=verify_m68444gx_Gq0VrCrt_d5ci_4c7w_9lvw_DLf0Tzm5lfPr; xgplayer_user_id=35623604631; fpk1=U2FsdGVkX19IzJrLMVLaQ1jXKriz7rqPqte525cP69dCTWXYrcu2qJY0aqEcJBtA4HgTQC87RXUAkDjwmlTtGQ==; fpk2=2d3bcfcec0eb62f24aad5cce4f806ba3; passport_csrf_token=a5b9d6bb8a4769a270a8fbaa43e8163d; passport_csrf_token_default=a5b9d6bb8a4769a270a8fbaa43e8163d; UIFID=481cde0aefb5fd66a02e3857c765c11a58536e172336c332084172243d11b41a47622cb44cc78c3273f254566da43afb8814376edcdc3c57671d892c55e2e218336f2903f8db99cd8ee0663a7b0289f60d29a75f842b92eff7edc1599d04be2826a992f0ae25f9ed24504c5caf604cfc5c5c4a7eec66ec78d215344fe74818fdd38a7b491bac00bfce8fb3eb90b215bf2b64e640a26c15a3a93c48dce05625a9; __security_mc_1_s_sdk_crypt_sdk=4a59d900-42e5-b894; bd_ticket_guard_client_web_domain=2; FORCE_LOGIN=%7B%22videoConsumedRemainSeconds%22%3A180%2C%22isForcePopClose%22%3A1%7D; stream_player_status_params=%22%7B%5C%22is_auto_play%5C%22%3A0%2C%5C%22is_full_screen%5C%22%3A0%2C%5C%22is_full_webscreen%5C%22%3A0%2C%5C%22is_mute%5C%22%3A0%2C%5C%22is_speed%5C%22%3A1%2C%5C%22is_visible%5C%22%3A0%7D%22; download_guide=%223%2F20250123%2F1%22; volume_info=%7B%22isUserMute%22%3Afalse%2C%22isMute%22%3Atrue%2C%22volume%22%3A0.5%7D; csrf_session_id=f5d3a4bcb500df3420f776403ecdd7bf; passport_mfa_token=CjU5xzkvqww07GCP5ujxgrt6bcsgJHX%2BQaRuWJusINpMaCJMTtqxZhyyMg5C2bySSwHGN%2FmTMBpKCjzdOspbKclvFOOzU6NlY90Og3fJ4I0zevyZjiLyKIl16bg3Su9JiSEk2GF0CTEWv2dQRJaDzO3gBj%2F8WHcQwsnnDRj2sdFsIAIiAQOcTpoU; d_ticket=90c2b0dbf4375a01d02e7b8064079d3cf3f2c; n_mh=Z5Gf-qhX2R2_a0fBJVLKq3qIuuFphJrW0EWoN4E4qZU; sso_auth_status=644076c75c4c287098fb9f4b510c5fff; sso_auth_status_ss=644076c75c4c287098fb9f4b510c5fff; __security_mc_1_s_sdk_cert_key=9543dbdf-42a3-afd2; is_staff_user=false; SelfTabRedDotControl=%5B%7B%22id%22%3A%227267026597171955764%22%2C%22u%22%3A85%2C%22c%22%3A0%7D%5D; publish_badge_show_info=%220%2C0%2C0%2C1737596848831%22; _bd_ticket_crypt_doamin=2; __security_server_data_status=1; biz_trace_id=94dfe8bd; passport_assist_user=CjymXSJeZOb30LcIsuA4QPmjKRh4GTTS3rt2hfoEw4PzjsaCh-ggDYA9uHhjcSZZWa1xpJ-ZBqedfUIEgBAaSgo8ZMqAysYMmDcEPicwZkueMK16K2uNO5oOm-Y69iG2cDjLLEXbc7cRh0ZV08QGv1sWTwGrfrKv8zS7tD2UELbJ5w0Yia_WVCABIgEDWQbm7Q%3D%3D; sso_uid_tt=5a38c9b0bd2ce7cf084a033c69bc4c31; sso_uid_tt_ss=5a38c9b0bd2ce7cf084a033c69bc4c31; toutiao_sso_user=afcb04924f4e0794b1db1498be7394bc; toutiao_sso_user_ss=afcb04924f4e0794b1db1498be7394bc; sid_ucp_sso_v1=1.0.0-KDBhNTBhMWFkMzAyNzQzNTNmYzY5YjQyMDI2M2Q1ZDkzMzkxYjY1ZDEKHwisgcCG8AIQj8DGvAYY7zEgDDCbwYDYBTgGQPQHSAYaAmxxIiBhZmNiMDQ5MjRmNGUwNzk0YjFkYjE0OThiZTczOTRiYw; ssid_ucp_sso_v1=1.0.0-KDBhNTBhMWFkMzAyNzQzNTNmYzY5YjQyMDI2M2Q1ZDkzMzkxYjY1ZDEKHwisgcCG8AIQj8DGvAYY7zEgDDCbwYDYBTgGQPQHSAYaAmxxIiBhZmNiMDQ5MjRmNGUwNzk0YjFkYjE0OThiZTczOTRiYw; __security_mc_1_s_sdk_sign_data_key_sso=adffdbb9-44cf-b7e4; login_time=1737596945201; passport_auth_status=c06eecb5dd21cf688bec989059f0a5b1%2Ceb73f030c0d3ad9a2786739c4d530dbe; passport_auth_status_ss=c06eecb5dd21cf688bec989059f0a5b1%2Ceb73f030c0d3ad9a2786739c4d530dbe; uid_tt=2882036411fdd8aefdb3fc86e42a6a8d; uid_tt_ss=2882036411fdd8aefdb3fc86e42a6a8d; sid_tt=6554becfe7a5e91de82907cbf799bcce; sessionid=6554becfe7a5e91de82907cbf799bcce; sessionid_ss=6554becfe7a5e91de82907cbf799bcce; _bd_ticket_crypt_cookie=8b79d715df6ecbbea03703d1998846fe; __security_mc_1_s_sdk_sign_data_key_web_protect=f2b1c6ca-4b4a-9a97; sid_guard=6554becfe7a5e91de82907cbf799bcce%7C1737596955%7C5183990%7CMon%2C+24-Mar-2025+01%3A49%3A05+GMT; sid_ucp_v1=1.0.0-KGI1NjQ0MTA2NWU2MGJkYWY5NjkxYTFhMDE4MjViOWZmZWRjOTk2MWMKGQisgcCG8AIQm8DGvAYY7zEgDDgGQPQHSAQaAmxxIiA2NTU0YmVjZmU3YTVlOTFkZTgyOTA3Y2JmNzk5YmNjZQ; ssid_ucp_v1=1.0.0-KGI1NjQ0MTA2NWU2MGJkYWY5NjkxYTFhMDE4MjViOWZmZWRjOTk2MWMKGQisgcCG8AIQm8DGvAYY7zEgDDgGQPQHSAQaAmxxIiA2NTU0YmVjZmU3YTVlOTFkZTgyOTA3Y2JmNzk5YmNjZQ; stream_recommend_feed_params=%22%7B%5C%22cookie_enabled%5C%22%3Atrue%2C%5C%22screen_width%5C%22%3A1920%2C%5C%22screen_height%5C%22%3A1080%2C%5C%22browser_online%5C%22%3Atrue%2C%5C%22cpu_core_num%5C%22%3A12%2C%5C%22device_memory%5C%22%3A8%2C%5C%22downlink%5C%22%3A10%2C%5C%22effective_type%5C%22%3A%5C%224g%5C%22%2C%5C%22round_trip_time%5C%22%3A100%7D%22; FOLLOW_NUMBER_YELLOW_POINT_INFO=%22MS4wLjABAAAAPbMzfNWV7J1xnl-zQOmpmBOYIskhKsGIT0Mg-NUTz1k%2F1737648000000%2F0%2F0%2F1737620523486%22; bd_ticket_guard_client_data=eyJiZC10aWNrZXQtZ3VhcmQtdmVyc2lvbiI6MiwiYmQtdGlja2V0LWd1YXJkLWl0ZXJhdGlvbi12ZXJzaW9uIjoxLCJiZC10aWNrZXQtZ3VhcmQtcmVlLXB1YmxpYy1rZXkiOiJCRVF2MHU4akIxSVQxVWhTZVNac0N6bVUvakxwZWNvUDE2WHhFRlJYZWdKZ2JnZVhlMGorc0xRRU9SY0pQUW9sNzlPeGRiOGFwdFB3cFlHVWxSK0loQXM9IiwiYmQtdGlja2V0LWd1YXJkLXdlYi12ZXJzaW9uIjoyfQ%3D%3D; WallpaperGuide=%7B%22showTime%22%3A1737563047899%2C%22closeTime%22%3A0%2C%22showCount%22%3A1%2C%22cursor1%22%3A35%2C%22cursor2%22%3A10%7D; odin_tt=4245df39541d639344d5d31469ee7f5efc678bee0fd1921499576d9cc4c16f0001ff6141729a301afaf7db439da1f636; passport_fe_beating_status=false; __ac_nonce=06792052300bb0e59ec9d; __ac_signature=_02B4Z6wo00f01xS1zHQAAIDDHzlyM7f7wacUlcjAAKLJPQ0QuHGFXrwYYgmTb2DUfhLIXNHRQibxOVSt5YB0YHMnZXsgjU5dXl-fOp4XR11sIE4j5BxmU25Qx5fFdduUKTfXyOccvzyJaCoP97; IsDouyinActive=true; home_can_add_dy_2_desktop=%220%22",
        }
        self.get_html()
        self.parse_video_info()
        self.init_workspace()
        self.get_video()

    def get_html(self):
        response = requests.get(self.url, headers=self.headers)
        if response.status_code == 200:
            self.html = response.text
        else:
            logger.error(f'下载html错误, http status code:{response.status_code}')

    def parse_video_info(self):
        pattern = r'<script id="RENDER_DATA" type="application/json">(.*?)</script>'
        result = re.search(pattern, self.html)
        if result is not None:
            decoded_data = urllib.parse.unquote(result.group(1))
            json_data = json.loads(decoded_data)
            self.video_url = f"http:{json_data['app']['videoDetail']['video']['playAddr'][0]['src']}"
            self.author = json_data['app']['videoDetail']['authorInfo']['nickname']
            desc = json_data['app']['videoDetail']['desc']
            response = re.search(r'^(.*?)$', desc)
            self.video_name = response.group(1).strip()
            logger.info(f'解析出视频地址：{self.video_url}, 视频名称：{self.video_name}')
        else:
            logger.error('解析视频信息出错')
    def get_video(self):
        logger.info('开始下载视频...')
        response = requests.get(self.video_url, headers=self.headers)
        if response.status_code == 200:
            _name = f'{self.video_name}-{self.author}.mp4'
            with open(os.path.join(self.workspace, _name), 'wb') as f:
                f.write(response.content)
                logger.info('保存视频成功')
        else:
            logger.error(response.status_code)


if __name__ == '__main__':
    url = 'https://www.douyin.com/user/MS4wLjABAAAAkiq8LIkcpNLZO-oRIVLYiAT7cy6Fqf8rc_gRfyb-cNs?from_tab_name=main&modal_id=7427263655978323235'
    downloader = DouyinDownloader()
    downloader.download(url)
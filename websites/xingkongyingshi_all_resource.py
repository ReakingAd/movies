import time
from loguru import logger
import pymysql
import pymysql.cursors
import requests
from bs4 import BeautifulSoup
import sys
"""
# 电影
名称，状态，更新，年份，地区，类型，语言，简介，可选清晰度
xkvvv_id, 分类：（电影、电视剧、综艺、动漫），图片
# 电视剧
名称，状态，更新，年份，地区，类型，语言，简介，可选清晰度
"""
log_format = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
logger.remove()
logger.add(sys.stdout, level="INFO", format=log_format) # 添加日志处理器，并指定输出格式
logger.add("logs/xkvvv.log", level="DEBUG", rotation="100 MB", retention="7 days", compression="zip")

class ParseError(Exception):
    pass

def parse_html(html, resource_id):
    soup = BeautifulSoup(html, 'lxml')
    info_list = []
    info_list.append(resource_id) # id
    try:
        name = soup.select_one('h2.hl-dc-title.hl-data-menu').text # 资源名称
        info_list.append(name)
    except Exception as e:
        logger.error(f'解析资源名称错误：{resource_id}-{e}')
        raise ParseError('解析资源名称错误,')
    
    li_list = soup.select('div.hl-detail-content div.hl-full-box ul.clearfix li')
    for index, li in enumerate(li_list):
        if index == 1:
            status = li.select_one("span.hl-text-conch").get_text(strip=True)
            info_list.append(status) # 状态
        elif index == 2:
            update_time = li.find('em', class_='hl-text-muted').next_sibling.strip()
            info_list.append(update_time) # 更新
        elif index == 3:
            year = li.find('em', class_='hl-text-muted').next_sibling.strip()
            info_list.append(year) # 年份
        elif index == 4:
            region = li.find('em', class_='hl-text-muted').next_sibling.strip()
            info_list.append(region) # 地区
        elif index == 5:
            genre = li.find('em', class_='hl-text-muted').next_sibling.strip()
            info_list.append(genre) # 类型
        elif index == 6:
            language = li.find('em', class_='hl-text-muted').next_sibling.strip()
            info_list.append(language) # 语言
        elif index == 7:
            description = li.find('em', class_='hl-text-muted').next_sibling.strip()
            info_list.append(description) # 简介
    # resolution 分辨率
    resolution_els = soup.select('a.hl-tabs-btn.hl-slide-swiper')
    resolution_list = [] 
    for resolution_el in resolution_els:
        text = resolution_el.getText(strip=True)
        resolution_list.append(text)
    info_list.append('|'.join(resolution_list))
    # category 分类
    category = soup.select_one('ul.hl-nav a.hl-text-conch.active').getText(strip=True)
    info_list.append(category)
    # image_url 图片地址
    pic_url = soup.select_one('span.hl-item-thumb.hl-lazy').get('data-original', '')
    # print(f'pic={pic}')
    info_list.append(pic_url)
    # print(info_list)

    info_tuple = tuple(info_list)
    return info_tuple

def save_to_database(info_tuple, conn):
    # connection = pymysql.connect(
    #     host='192.168.112.129',
    #     user='root',
    #     password='Pass1234!@#$',
    #     database='xkvvv',
    #     charset='utf8mb4',
    #     cursorclass=pymysql.cursors.DictCursor
    # )
    try:
        with conn.cursor() as cursor:
            insert_sql = """
            insert into resource 
                (resource_id, name, status, update_time, year, region, genre, language, description, resolution, category, image_url)
            values
                (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_sql, info_tuple)
            conn.commit()
            print(f"插入成功, ID:{cursor.lastrowid}")
    except Exception as e:
        conn.rollback()
        print(f"插入失败：{str(e)}")
    # finally:
    #     connection.close()

def get_html(id):
    url = f'https://www.xkvvv.com/detail/{id}/'
    print(f'downloading {id}')
    for _ in range(1, 11):
        try:
            rsp = requests.get(url, timeout=5)
            html = rsp.text
            return html
        except Exception as e:
            logger.error(f'请求失败：{id} - {e}')
            time.sleep(5)
    else:
        logger.error(f"请求达到最大次数。{id} 失败")
        return None

if __name__ == '__main__':
    conn = pymysql.connect(
        host='192.168.112.129',
        user='root',
        password='Pass1234!@#$',
        database='xkvvv',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    i = 117000
    while True:
        if i >= 120_000:
            logger.error('循环次数达到了120000, 退出循环')
            break
        html = get_html(i)
        try:
            info_tuple = parse_html(html, i)
        except Exception as e:
            print(e)
            break
        save_to_database(info_tuple, conn)
        time.sleep(1)
        i += 1
        if html is None:
            continue
    conn.close()
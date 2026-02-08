from enum import Enum, unique
import json
import os
import queue
import random
import re
import sys
import threading
import time
import subprocess
import pymysql

import pymysql.cursors
import requests
from urllib.parse import urlparse, parse_qs
    
def test():
    connection = pymysql.connect(
        host='192.168.112.129',
        user='root',
        password='Pass1234!@#$',
        database='xkvvv',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    try:
        with connection.cursor() as cursor:
            select_sql = 'select * from video_resource'
            cursor.execute(select_sql)
            results = cursor.fetchall()
            print(results)
    finally:
        connection.close()

if __name__ == '__main__':
    test()


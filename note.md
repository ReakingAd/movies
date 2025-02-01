# pip 与 venv。为当前项目建立虚拟环境并管理依赖包

```python
python -m venv venv  # 创建虚拟环境
venv\Scripts\activate   # 进入虚拟环境

(venv): pip list # 查看当前环境下的依赖列表
(venv): pip install flask
(venv): pip freeze > requirements.txt
(venv): pip install
```

# TODO：学学yt-dlp的log写法
# TODO: 命令行参数形式调用
# TODO: 1. 删除多余的碎片文件
# TODO: 3. https://www.bilibili.com/video/BV1wZ421e7Fr?spm_id_from=333.788.videopod.episodes&vd_source=fda0d59c12dcd36c1eccec649fa28042&p=4
# driver = ChromiumPage()   
# driver.listen.start('api.bilibili.com/x/space/wbi/arc/search')
# driver.get('https://space.bilibili.com/3493110839511225/video')
# response = driver.listen.wait()
# TODO: 4. 与抓包工具结合？fiddler
# TODO: 5. 虎龙，快速搭建的电影网站，是从哪获得的那么多电影资源？
# TODO: bilibili插件，
    1. 记录什么时候，哪个视频关注的up
    2. 下载视频、下载音频
    3. 暗色模式
# TODO：cookie插件，保存符合Netscape format的文件cookies.txt
# TODO: 抖音： cookie怎么弄，手动获取复制进来，有没有自动的方法
# TODO：大漠插件？是按键精灵的插件吧
# TODO: 魔兽拍卖行auto量化交易。卖店价>拍卖价，套利
# TODO：股票模拟盘，测试量化交易
# TODO: syber 算命

# TODO: 1. 自动解析 网站 
# TODO: 直播录屏
    1. 迅捷屏幕录像工具：支持高清录制、灵活的录制区域选择、丰富的音频录制模式以及视频编辑功能。
    2. Camtasia：这是一款专业屏幕录制和视频编辑软件，支持全屏、窗口、区域等多种录制模式，并内置丰富的视频剪辑工具和特效。
    3. Loom：提供剪辑、音频调整、特效添加等多种编辑工具，支持多种视频格式和分辨率。
```python
import optparse

# TODO: bilibili插件： 我是因为哪个视频关注的这个up

def main():
    parser = optparse.OptionParser(usage="usage: %prog [options] arg1 arg2")

    parser.add_option("-f", "--file", dest="filename", help="read datafrom FILENAME")
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False, help="make lots of noise [default]")

    (options, args) = parser.parse_args()

    if options.verbose:
        print("Verbose mode is on")

    if options.filename:
        print(f"Reading data from {options.filename}")

    print(f"Positional arguments: {args}")

if __name__ == '__main__':
    main()
```

# 浏览器 hover 状态定格
### 方法一
找到指定元素，一定要是网页源代码绑定了:hover逻辑的元素才行。强制元素状态勾选上：hover，即可
### 方法二
1. 打开console，输入debugger先不要回车。
2. 鼠标放在绑定过:hover逻辑的元素，当出现:hover激活状态时，按回车使控制台中的debugger发出。此时浏览器会进入debugger状态，冻结。

# 生成器表达式，列表推导式
```python
# 二者语法上只在于用 [中括号] 还是 (小括号)
list = [x*2 for x in range(10)] # 列表推导式
gen  = (x*2 for x in range(10)) # 生成器表达式

# 可增加条件判断
list = [x*2 for x in range(10) if x<5] # 只有小于5的成员，才会乘以2作为组成新 list
gen  = (x*2 for x in range(10) if x<5) # 只有小于5的成员，才会乘以2作为组成新 generator
```
# 线程
1. 线程
```python
# test.py
def producer():
    for i in range(3):
        print(f'生成数据：{i}')
        time.sleep(1)
producer_thread = threading.Thread(target=producer)
producer_thread.start() # 子线程运行
producer_thread.join() # 主线程停在这里，等待子线程 producer_thread 运行结束
print('子进程运行完毕')
```
2. 两个子进程之间，使用queue共享数据
```python
import threading
import time
import queue

q = queue.Queue()

def producer():
    time.sleep(4)
    for i in range(3):
        q.put(i)
        print(f'生成数据：{i}')
        time.sleep(1)

producer_thread = threading.Thread(target=producer)

def comsumer():
    while True:
        item = q.get()
        if item is None:
            break
        print(f'消费数据：{item}')
        q.task_done()

consumer_thread = threading.Thread(target=comsumer)
consumer_thread.start()
producer_thread.start() # 子线程运行
producer_thread.join() # 主线程停在这里，等待子线程 producer_thread 运行结束

q.put(None)

consumer_thread.join()
print('All done>>>>>>')
```
```python
queue.task_done() 通知队列该任务完成。 会使队列中未完成任务的计数 -1
queue.put() 讲任务加入队列。会使队列中未完成任务的计数 +1
queue.join() 阻塞等待，知道队列未完成任务的计数为0 （即task_done()调用次数==put()调用次数）
```
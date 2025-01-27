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
# TODO: 插件，记录什么时候，哪个视频关注的up
# TODO：cookie插件，保存符合Netscape format的文件cookies.txt
# TODO: 抖音： cookie怎么弄，手动获取复制进来，有没有自动的方法

# TODO: 1. 自动解析 网站 
# TODO: 直播录屏
    1. 迅捷屏幕录像工具：支持高清录制、灵活的录制区域选择、丰富的音频录制模式以及视频编辑功能。
    2. Camtasia：这是一款专业屏幕录制和视频编辑软件，支持全屏、窗口、区域等多种录制模式，并内置丰富的视频剪辑工具和特效。
    3. Loom：提供剪辑、音频调整、特效添加等多种编辑工具，支持多种视频格式和分辨率。
```python
import optparse

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
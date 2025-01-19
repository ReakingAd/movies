from abc import ABC, abstractmethod
from urllib.error import URLError
from urllib.request import ProxyHandler, build_opener

import ffmpeg

# ffmpeg -i "F:\litao\workspace_py\download_videos\movies\哈利波特7HD中字版\downloads\f0015e42756000001.ts" "F:\litao\workspace_py\download_videos\movies\哈利波特7HD中字版\哈利波特7HD中字版.mp4"

(
    ffmpeg
        # .input('F:\\litao\\workspace_py\\download_videos\\movies\\哈利波特7HD中字版\\downloads\\f0015e42756000001.ts', format='concat', safe=0)
        # .input('concat_list.txt', format='concat', safe=0)
        .input('F:\\litao\\workspace_py\\download_videos\\movies\\哈利波特7HD中字版\\concat_list.txt', format='concat', safe=0)

        .output(f"123.mp4", vcodec='copy', acodec='copy')
        .run()
)

# stream = ffmpeg.input('concat_list.txt', format='concat', safe=0)
# print(stream)
# stream = ffmpeg.output(stream, 'F:\litao\workspace_py\download_videos\movies\哈利波特7HD中字版\哈利波特7HD中字版.mp4')
# print(stream)
# ffmpeg.run(stream)
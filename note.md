# pip 与 venv。为当前项目建立虚拟环境并管理依赖包

```python
python -m venv venv  # 创建虚拟环境
venv\Scripts\activate   # 进入虚拟环境

(venv): pip list # 查看当前环境下的依赖列表
(venv): pip install flask
(venv): pip freeze > requirements.txt
(venv): pip install
```

# TODO: 插件，记录什么时候，哪个视频关注的up
# TODO：cookie插件，保存符合Netscape format的文件cookies.txt
# TODO: 抖音： cookie怎么弄，手动获取复制进来，有没有自动的方法
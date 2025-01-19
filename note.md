# pip 与 venv。为当前项目建立虚拟环境并管理依赖包

```python
python -m venv venv  # 创建虚拟环境
venv\Scripts\activate   # 进入虚拟环境

(venv): pip list # 查看当前环境下的依赖列表
(venv): pip install flask
(venv): pip freeze > requirements.txt
(venv): pip install
```
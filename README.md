# stock_system_flask
股票统计系统-flask后台

## 运行方式
```bash
conda create -n flask python=3.7.10
conda activate flask
pip install -r requirements.txt
python main.py

bash start.sh  # 或者使用 nohup 的方式启动
```

## 错误和错误的解决方式
### ModuleNotFoundError: No module named 'flask._compat'
修改一下：flask_script/__init__.py 中的 
```python
# from ._compat import text_type 改成 from flask_script._compat import text_type
```
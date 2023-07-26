"""
全局的配置文件
"""
import os

# 模板配置
# ROOT_DIR = os.path.abspath(os.path.dirname('.'))

# STATIC_DIRECTORY = os.path.join(ROOT_DIR, "static")
# TEMPLATE_DIRECTORY = os.path.join(ROOT_DIR, "templates/order_system")

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TEMP_DIR = os.path.join(BASE_DIR, "../tmp")

MINIO_HOSTS = "127.0.0.1:9000"
ACCESS_KEY = "minioadmin"
SECRET_KEY = "minioadmin"

AUTH_SECRET_KEY = "9d7caa1575015bbbb5bfbd0bb82984a5e856dbc23050da4b4eecbf8e0de0d06a"
ALGORITHM = "HS256"
# 过期时间（分钟）
ACCESS_TOKEN_EXPIRE_MINUTES = 60

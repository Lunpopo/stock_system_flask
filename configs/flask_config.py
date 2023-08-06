"""
Flask 的启动配置文件
"""
# 基础设置
# --------snip--------
# 跟踪数据库的修改---->不建议开启，未来的版本中会移除
from urllib.parse import quote

SQLALCHEMY_TRACK_MODIFICATIONS = False
# 显示 sql 语句，调试阶段为True
SQLALCHEMY_ECHO = False

# 不要在生产环境使用debug
DEBUG = True

# 限制上传文件的大小
MAX_CONTENT_LENGTH = 1024 * 1024 * 10
# 验证上传文件名
UPLOAD_EXTENSIONS = ['.jpg', '.png', '.gif']
# --------snip--------

# csrf
# --------snip--------
CSRF_ENABLED = True
# 防止csrf的
SECRET_KEY = 'EjpNVSNQTyGi1VvWECj9TvC/+kq3oujee2kTfQUs8yCM6xX9Yjq52v54g+HVoknA'
# --------snip--------

# 数据库配置
# --------snip--------
# 配置数据库的地址
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{}:{}@{}:{}/stock_system_db'.format(
    "root", quote("5Q&%ngf:<N@=;r+$"), "162.14.83.226", "3306"
)
# --------snip--------


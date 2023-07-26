"""
flask启动文件
"""
from flask_migrate import MigrateCommand
from flask_script import Manager

from app_router import create_app
# from app_router.models.database import db

app, db = create_app()

if __name__ == '__main__':
    manager = Manager(app, db)
    manager.add_command("db", MigrateCommand)
    # python main.py runserver --host=0.0.0.0
    manager.run()


# """
# flask启动文件
# """
# from gevent import monkey
# monkey.patch_all()  # 替换标准socket模块的函数和类，改成异步非阻塞
#
# # 将python标准的io方法，都替换成gevent中同名的方法，遇到io阻塞gevent自动进行协程切换
# from app_router import create_app
#
# app = create_app()
#
#
# if __name__ == '__main__':
#     # 不能用自带的服务器
#     from gevent.pywsgi import WSGIServer
#     WSGIServer(("0.0.0.0", 5000), app).serve_forever()

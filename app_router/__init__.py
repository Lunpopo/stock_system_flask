"""
flask初始化
"""
from flask import Flask
from flask_cors import CORS

from app_router.data_display_bp.data_display import data_bp
from app_router.models import user_crud
from app_router.models.database import db
from app_router.models.models import DealerList
from app_router.order_display_bp.outbound_order import outbound_order_bp
from app_router.order_display_bp.purchase_order import purchase_order_bp
from app_router.order_display_bp.order_statistics import order_statistics_bp
from app_router.user_manager_bp.user_lib import get_current_ip
from app_router.user_manager_bp.user_manage import user_bp
from configs import flask_config
from utils.authentication import pwd_context


def init_db_data():
    """
    初始化数据库数据
    """
    from app_router.models import crud

    # 添加管理员用户组
    group_name_list = [
        # 普通用户组
        'editor',
        # 用户管理组
        'user',
        # 数据管理组
        'data',
        # 管理员
        'admin'
    ]
    for group_name in group_name_list:
        group_data = {
            "group_name": group_name
        }
        if not user_crud.get_group_by_name(group_name):
            user_crud.add_group(data=group_data)

    # 注册管理员用户
    user_data = {
        "username": "admin",
        "password": pwd_context.hash("111111"),
        "group_id": user_crud.get_group_by_name(group_name='admin').business_id,
        "register_ip": get_current_ip(),
        "status": 0
    }
    if not user_crud.get_user_by_name(username='admin'):
        user_crud.add_user(data=user_data)

    # 注册编辑人员用户
    user_data = {
        "username": "editor",
        "password": pwd_context.hash("111111"),
        "group_id": user_crud.get_group_by_name(group_name='editor').business_id,
        "register_ip": get_current_ip(),
        "status": 0
    }
    if not user_crud.get_user_by_name(username='editor'):
        user_crud.add_user(data=user_data)


def create_app():
    """
    创建app
    :return:
    """
    app = Flask(__name__, static_url_path='/static', template_folder='templates/order_system')
    CORS(app, supports_credentials=True)
    app.config.from_object(flask_config)
    # 注册蓝图
    app.register_blueprint(data_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(order_statistics_bp)
    app.register_blueprint(purchase_order_bp)
    app.register_blueprint(outbound_order_bp)
    db.init_app(app=app)
    return app

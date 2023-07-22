import json
import time
from datetime import timedelta

from flask import Blueprint, request
from gkestor_common_logger import Logger
from jose import ExpiredSignatureError

from app_router.models import user_crud
from app_router.user_manager_bp.user_lib import check_user, generate_routes, filter_routes_by_role, get_current_ip
from configs.contents import ACCESS_TOKEN_EXPIRE_MINUTES
from enums.enums import AuthCheckEnum
from messages.messages import *
from utils import restful
from utils.authentication import create_access_token, decode_token, auth_check
from utils.date_utils import time_to_timestamp

user_bp = Blueprint("user_manage", __name__, url_prefix="/user")
logger = Logger()


@user_bp.route('/asyn', methods=['GET'])
def test_asyn_one():
    time.sleep(3)
    return restful.ok(message='hello asyn')


@user_bp.route("/login", methods=["POST"])
def login():
    """
    用户登录
    :return:
    """
    data = request.get_data(as_text=True)
    params_dict = json.loads(data)
    username = params_dict.get("username")
    password = params_dict.get('password')

    user = check_user(username, password)
    if not user:
        return restful.server_error(message="用户名或密码错误！")

    # 过期时间（分钟）
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    data = {
        "token": "Bearer:{}".format(create_access_token(user.business_id, expires_delta=access_token_expires))
    }
    return restful.ok(message='登录成功！', data=data)


@user_bp.route("/delete_user", methods=["POST"])
def delete_user():
    """
    删除用户api
    :return:
    """
    auth_status = auth_check(user_token=request.headers.get('Authorization'), api='user/delete_user')
    if AuthCheckEnum[auth_status].value is not True:
        return AuthCheckEnum[auth_status].value

    data = request.get_data(as_text=True)
    params_dict = json.loads(data)
    username = params_dict.get("username")

    user = user_crud.get_user_by_name(username)
    if user:
        # 删除用户
        user_crud.delete_user(username)
    else:
        return restful.server_error(message=delete_user_failed, data=username)
    return restful.ok(message=delete_user_success, data=username)


@user_bp.route("/create_user", methods=["POST"])
def create_user():
    """
    新增用户api
    :return:
    """
    auth_status = auth_check(user_token=request.headers.get('Authorization'), api='user/create_user')
    if AuthCheckEnum[auth_status].value is not True:
        return AuthCheckEnum[auth_status].value

    data = request.get_data(as_text=True)
    params_dict = json.loads(data)
    username = params_dict.get("username")
    password = params_dict.get('password')
    group_name = params_dict.get('group_name')
    add_user_dict = {
        'username': username,
        'password': password,
        "register_ip": get_current_ip(),
        "status": 0
    }

    user = user_crud.get_user_by_name(username)
    if not user:
        # 新增用户
        # 查询组所在地
        group_obj = user_crud.get_group_by_name(group_name)
        if group_obj is None:
            return restful.server_error(message=add_user_failed, data={'group_name': group_name})
        add_user_dict['group_id'] = group_obj.business_id
        user_crud.add_user(add_user_dict)
    else:
        return restful.server_error(message=add_user_failed, data=username)
    return restful.ok(message=add_user_success, data=username)


@user_bp.route("/update_user", methods=["POST"])
def update_user():
    """
    更新用户api
    :return:
    """
    auth_status = auth_check(user_token=request.headers.get('Authorization'), api='user/update_user')
    if AuthCheckEnum[auth_status].value is not True:
        return AuthCheckEnum[auth_status].value

    data = request.get_data(as_text=True)
    params_dict = json.loads(data)
    username = params_dict.get("username")
    password = params_dict.get('password')
    group_name = params_dict.get('group_name')
    update_user_dict = {
        'username': username,
        'password': password,
        "register_ip": get_current_ip(),
        "status": 0
    }

    user = user_crud.get_user_by_name(username)
    if user:
        # 查询组所在地
        group_obj = user_crud.get_group_by_name(group_name)
        if group_obj is None:
            return restful.server_error(message=update_user_failed, data={'group_name': group_name})
        update_user_dict['group_id'] = group_obj.business_id
        user_crud.update_user(update_user_dict)
    else:
        return restful.server_error(message=update_user_failed, data=username)
    return restful.ok(message=update_user_success, data=username)


@user_bp.route("/info", methods=["GET"])
def user_info():
    """
    获取用户信息 api
    :return:
    """
    auth_status = auth_check(user_token=request.headers.get('Authorization'), api='user/info')
    if AuthCheckEnum[auth_status].value is not True:
        return AuthCheckEnum[auth_status].value

    try:
        user_token = request.headers.get('Authorization')
        user_token = user_token.split("Bearer:")[-1]
        decode_token_dict = decode_token(user_token)
        user_id = decode_token_dict.get("sub")
        group_obj = user_crud.get_group_obj_by_user_id(user_id=user_id)
        return_user_obj = {
            "roles": [group_obj.group_name],
            'introduction': group_obj.description,
            'avatar': 'https://wpimg.wallstcn.com/f778738c-e4f8-4870-b634-56703b4acafe.gif',
            'name': group_obj.group_label
        }
        return restful.ok(message="获取用户信息成功！", data=return_user_obj)
    except ExpiredSignatureError:
        return restful.token_expired(message="登录过期！")
    except:
        return restful.illegal_token(message="非法登录！")


@user_bp.route("roles", methods=["GET"])
def get_roles():
    """
    获取角色权限信息表
    :return:
    """
    auth_status = auth_check(user_token=request.headers.get('Authorization'), api='user/roles')
    if AuthCheckEnum[auth_status].value is not True:
        return AuthCheckEnum[auth_status].value

    result = user_crud.get_all_role()
    data_list = [_.as_dict() for _ in result]
    # 统一转换成时间戳的形式
    data_list = time_to_timestamp(data_list)

    return_data = {
        "Success": True,
        "code": 2000,
        "msg": "",
        "data": data_list
    }
    return restful.ok(message="获取角色权限信息成功！", data=return_data)


@user_bp.route("update_role", methods=["POST"])
def update_role():
    """
    更新 角色 和 所对应的前端路由
    :return:
    """
    auth_status = auth_check(user_token=request.headers.get('Authorization'), api='user/update_role')
    if AuthCheckEnum[auth_status].value is not True:
        return AuthCheckEnum[auth_status].value

    data = request.get_data(as_text=True)
    params_dict = json.loads(data)
    logger.info(
        "/user/add_role 前端传入的参数为：\n{}".format(json.dumps(params_dict, indent=4, ensure_ascii=False))
    )
    roles_routes = params_dict.get('routes')
    group_name = params_dict.get('group_name')
    group_label = params_dict.get('group_label')
    description = params_dict.get('description')
    business_id = params_dict.get('business_id')

    update_group_dict = {
        "group_name": group_name,
        "group_label": group_label,
        "description": description,
        'business_id': business_id
    }
    try:
        group_obj = user_crud.update_role_and_route(update_group_dict, roles_routes)
        return_data_dict = group_obj.as_dict()
        return restful.ok(message=update_role_success, data=return_data_dict)
    except:
        return restful.server_error(message=update_role_failed, data=update_group_dict)


@user_bp.route("add_role", methods=["POST"])
def add_role():
    """
    新增 角色 和 所对应的路由
    :return:
    """
    auth_status = auth_check(user_token=request.headers.get('Authorization'), api='user/add_role')
    if AuthCheckEnum[auth_status].value is not True:
        return AuthCheckEnum[auth_status].value

    data = request.get_data(as_text=True)
    params_dict = json.loads(data)
    logger.info(
        "/user/add_role 前端传入的参数为：\n{}".format(json.dumps(params_dict, indent=4, ensure_ascii=False))
    )
    roles_routes = params_dict.get('routes')
    group_name = params_dict.get('group_name')
    group_label = params_dict.get('group_label')
    description = params_dict.get('description')

    add_group_dict = {
        "group_name": group_name,
        "group_label": group_label,
        "description": description,
    }
    try:
        group_obj = user_crud.add_role_and_route(add_group_dict, roles_routes)
        return_data_dict = group_obj.as_dict()
        return restful.ok(message=add_role_success, data=return_data_dict)
    except:
        return restful.server_error(message=add_role_failed, data=add_group_dict)


@user_bp.route("delete_role", methods=["POST"])
def delete_role():
    """
    删除角色
    :return:
    """
    auth_status = auth_check(user_token=request.headers.get('Authorization'), api='user/delete_role')
    if AuthCheckEnum[auth_status].value is not True:
        return AuthCheckEnum[auth_status].value

    data = request.get_data(as_text=True)
    params_dict = json.loads(data)
    logger.info(
        "/user/delete_role 前端传入的参数为：\n{}".format(json.dumps(params_dict, indent=4, ensure_ascii=False))
    )
    role_id = params_dict.get('role_id')
    group_name = params_dict.get('group_name')
    try:
        user_crud.delete_role_and_route(role_id, group_name)
    except:
        return restful.server_error(message=delete_role_failed)
    return restful.ok(message=delete_role_success)


@user_bp.route("get_view_routes", methods=["GET"])
def get_view_routes():
    """
    获取前端的路由表-并且根据role进行过滤
    :return:
    """
    auth_status = auth_check(user_token=request.headers.get('Authorization'), api='user/get_view_routes')
    if AuthCheckEnum[auth_status].value is not True:
        return AuthCheckEnum[auth_status].value

    user_token = request.headers.get('Authorization')
    user_token = user_token.split("Bearer:")[-1]
    decode_token_dict = decode_token(user_token)
    user_id = decode_token_dict.get("sub")
    # 当前登录的角色
    group_obj = user_crud.get_group_obj_by_user_id(user_id=user_id)

    all_menu_list = user_crud.get_all_menu()
    # 返回所有的vue前端可用的路由列表（需要根据角色进行过滤）
    all_routes_list = generate_routes(all_menu_list)
    # 根据角色过滤返回结果
    filter_routes = filter_routes_by_role(all_routes_list, group_obj.group_name)
    return restful.ok(message="返回前端路由信息", data=filter_routes)


@user_bp.route("get_all_permission", methods=["GET"])
def get_all_permission():
    """
    获取所有的api权限组
    :return:
    """
    auth_status = auth_check(user_token=request.headers.get('Authorization'), api='user/get_all_permission')
    if AuthCheckEnum[auth_status].value is not True:
        return AuthCheckEnum[auth_status].value

    group_names = user_crud.get_all_permission()
    return_data = {
        "Success": True,
        "code": 2000,
        "msg": "",
        "data": group_names
    }
    return restful.ok(message="返回所有的api权限", data=return_data)


@user_bp.route("get_parent_menu", methods=["GET"])
def get_parent_menu():
    """
    获取所有的父级菜单
    :return:
    """
    auth_status = auth_check(user_token=request.headers.get('Authorization'), api='user/get_parent_menu')
    if AuthCheckEnum[auth_status].value is not True:
        return AuthCheckEnum[auth_status].value

    result = user_crud.get_parent_menu()
    # json格式化
    data_list = [_.as_dict() for _ in result]
    # 统一转换成时间戳的形式
    data_list = time_to_timestamp(data_list)

    return_data = {
        "Success": True,
        "code": 2000,
        "msg": "",
        "data": data_list
    }
    return restful.ok(message="返回所有的父级菜单列表数据", data=return_data)


@user_bp.route("routes", methods=["GET"])
def routes():
    """
    获取所有的菜单（api）也即路由
    :return:
    """
    auth_status = auth_check(user_token=request.headers.get('Authorization'), api='user/routes')
    if AuthCheckEnum[auth_status].value is not True:
        return AuthCheckEnum[auth_status].value

    all_menu_list = user_crud.get_all_menu()
    # 返回所有的vue前端可用的路由列表（需要根据角色进行过滤）
    all_routes_list = generate_routes(all_menu_list)
    return restful.ok(message="获取所有的菜单（api）成功！", data=all_routes_list)


@user_bp.route("get_routes_by_role", methods=["GET"])
def get_routes_by_role():
    """
    获取该名角色所拥有的路由
    :return:
    """
    auth_status = auth_check(user_token=request.headers.get('Authorization'), api='user/get_routes_by_role')
    if AuthCheckEnum[auth_status].value is not True:
        return AuthCheckEnum[auth_status].value

    role = request.args.get("role")
    all_menu_list = user_crud.get_all_menu()
    # 返回所有的vue前端可用的路由列表（需要根据角色进行过滤）
    all_routes_list = generate_routes(all_menu_list)
    # 根据角色过滤返回结果
    filter_routes = filter_routes_by_role(all_routes_list, role)
    return restful.ok(message="获取 {} 对应的路由完成！".format(role), data=filter_routes)


@user_bp.route("search_api", methods=["GET"])
def search_api():
    """
    搜索api功能
    :return:
    """
    auth_status = auth_check(user_token=request.headers.get('Authorization'), api='user/search_api')
    if AuthCheckEnum[auth_status].value is not True:
        return AuthCheckEnum[auth_status].value

    title = request.args.get("title")
    page = int(request.args.get("page"))
    limit = int(request.args.get("limit"))

    params_dict = {"title": title, 'page': page, 'limit': limit}
    logger.info("/user/search_api 前端的入参参数：\n{}".format(json.dumps(params_dict, indent=4, ensure_ascii=False)))

    # 前端page从1开始
    page -= 1
    page = page * limit
    result = user_crud.search_api(title, page, limit)

    result_data = result.get("data")
    data_list = time_to_timestamp(result_data)

    return_data = {
        "Success": True,
        "code": 2000,
        "msg": "",
        "count": result.get('count'),
        "data": data_list
    }
    return restful.ok(message="返回功能api列表数据", data=return_data)


@user_bp.route("get_menu", methods=["GET"])
def get_menu():
    """
    获取菜单列表
    :return:
    """
    auth_status = auth_check(user_token=request.headers.get('Authorization'), api='user/get_menu')
    if not AuthCheckEnum[auth_status].value:
        return AuthCheckEnum[auth_status].value

    page = int(request.args.get("page"))
    limit = int(request.args.get("limit"))

    params_dict = {"page": page, "limit": limit}
    logger.info("/user/get_menu 前端的入参参数：\n{}".format(json.dumps(params_dict, indent=4, ensure_ascii=False)))

    # 前端page从1开始
    page -= 1
    page = page * limit
    result = user_crud.get_menu(page, limit)

    result_data = result.get("data")
    data_list = time_to_timestamp(result_data)

    return_data = {
        "Success": True,
        "code": 2000,
        "msg": "",
        "count": result.get('count'),
        "data": data_list
    }
    return restful.ok(message="返回菜单列表数据", data=return_data)


@user_bp.route("delete_menu", methods=["POST"])
def delete_menu():
    """
    删除菜单
    :return:
    """
    auth_status = auth_check(user_token=request.headers.get('Authorization'), api='user/delete_menu')
    if AuthCheckEnum[auth_status].value is not True:
        return AuthCheckEnum[auth_status].value

    data = request.get_data(as_text=True)
    params_dict = json.loads(data)
    logger.info(
        "/user/delete_menu 前端传入的参数为：\n{}".format(json.dumps(params_dict, indent=4, ensure_ascii=False))
    )
    menu_id = params_dict.get("business_id")
    try:
        if menu_id:
            user_crud.delete_menu_by_id(menu_id)
    except:
        return restful.server_error(message=delete_menu_failed)
    return restful.ok(message=delete_menu_success)


@user_bp.route("delete_api", methods=["POST"])
def delete_api():
    """
    删除功能api
    :return:
    """
    auth_status = auth_check(user_token=request.headers.get('Authorization'), api='user/delete_api')
    if AuthCheckEnum[auth_status].value is not True:
        return AuthCheckEnum[auth_status].value

    data = request.get_data(as_text=True)
    params_dict = json.loads(data)
    logger.info(
        "/user/delete_api 前端传入的参数为：\n{}".format(json.dumps(params_dict, indent=4, ensure_ascii=False))
    )
    api_id = params_dict.get("business_id")
    try:
        if api_id:
            user_crud.delete_api_by_id(api_id)
    except:
        return restful.server_error(message=delete_api_failed)
    return restful.ok(message=delete_api_success)


@user_bp.route("add_api", methods=["POST"])
def add_api():
    """
    新增功能api
    :return:
    """
    auth_status = auth_check(user_token=request.headers.get('Authorization'), api='user/add_api')
    if AuthCheckEnum[auth_status].value is not True:
        return AuthCheckEnum[auth_status].value

    data = request.get_data(as_text=True)
    params_dict = json.loads(data)
    logger.info(
        "/user/add_api 前端传入的参数为：\n{}".format(json.dumps(params_dict, indent=4, ensure_ascii=False))
    )
    api_name = params_dict.get("api_name")
    title = params_dict.get("title")
    description = params_dict.get("description")
    permission_list = params_dict.get("permission")
    # permission传过来是个数组，需要变换成字符串
    permission_list = [str(x) for x in permission_list]
    permission = ":".join(permission_list)

    try:
        if title:
            add_api_dict = {
                "api_name": api_name,
                "title": title,
                "permission": permission,
                "description": description
            }
            # 新增一条功能api
            api_title = user_crud.add_api(data=add_api_dict)

            if api_title:
                return restful.ok(message=add_api_success, data=api_title)
            else:
                return restful.server_error(message=add_api_failed)
    except:
        return restful.server_error(message=add_api_failed)


@user_bp.route("add_menu", methods=["POST"])
def add_menu():
    """
    新增菜单
    :return:
    """
    auth_status = auth_check(user_token=request.headers.get('Authorization'), api='user/add_menu')
    if AuthCheckEnum[auth_status].value is not True:
        return AuthCheckEnum[auth_status].value

    data = request.get_data(as_text=True)
    params_dict = json.loads(data)
    logger.info(
        "/user/add_menu 前端传入的参数为：\n{}".format(json.dumps(params_dict, indent=4, ensure_ascii=False))
    )
    api_parent_id = params_dict.get("api_parent_id")
    title = params_dict.get("title")
    vue_name = params_dict.get("vue_name")
    description = params_dict.get("description")
    icon = params_dict.get("icon")
    redirect = params_dict.get("redirect")
    menu_type = params_dict.get("menu_type")
    hidden = params_dict.get("hidden")
    permission_list = params_dict.get("permission")
    # permission传过来是个数组，需要变换成字符串
    permission_list = [str(x) for x in permission_list]
    permission = ":".join(permission_list)
    router_path = params_dict.get("router_path")
    component_path = params_dict.get("component_path")

    try:
        if title:
            add_menu_dict = {
                "api_parent_id": api_parent_id,
                "title": title,
                'vue_name': vue_name,
                "description": description,
                "icon": icon,
                'redirect': redirect,
                "menu_type": menu_type,
                "hidden": hidden,
                "permission": permission,
                "router_path": router_path,
                "component_path": component_path,
            }
            # 新增一条菜单
            menu_title = user_crud.add_menu(data=add_menu_dict)

            if menu_title:
                return restful.ok(message=add_menu_success, data=menu_title)
            else:
                return restful.server_error(message=add_menu_failed)
    except:
        return restful.server_error(message=add_menu_failed)


@user_bp.route("update_api", methods=["POST"])
def update_api():
    """
    更新功能api
    :return:
    """
    auth_status = auth_check(user_token=request.headers.get('Authorization'), api='user/update_api')
    if AuthCheckEnum[auth_status].value is not True:
        return AuthCheckEnum[auth_status].value

    data = request.get_data(as_text=True)
    params_dict = json.loads(data)
    logger.info(
        "/user/update_api 前端传入的参数为：\n{}".format(json.dumps(params_dict, indent=4, ensure_ascii=False))
    )
    api_name = params_dict.get("api_name")
    title = params_dict.get("title")
    description = params_dict.get("description")
    permission_list = params_dict.get("permission")
    # permission传过来是个数组，需要变换成字符串
    permission_list = [str(x) for x in permission_list]
    permission = ":".join(permission_list)
    business_id = params_dict.get('business_id')

    try:
        if title:
            update_api_dict = {
                "api_name": api_name,
                "title": title,
                "permission": permission,
                "description": description,
                "business_id": business_id
            }
            # 更新一条功能api
            user_crud.update_api(data=update_api_dict)
            return restful.ok(message=update_api_success)
    except:
        logger.error(update_api_failed)
        return restful.server_error(message=update_api_failed)


@user_bp.route("update_menu", methods=["POST"])
def update_menu():
    """
    更新菜单
    :return:
    """
    auth_status = auth_check(user_token=request.headers.get('Authorization'), api='user/update_menu')
    if AuthCheckEnum[auth_status].value is not True:
        return AuthCheckEnum[auth_status].value

    data = request.get_data(as_text=True)
    params_dict = json.loads(data)
    logger.info(
        "/user/update_menu 前端传入的参数为：\n{}".format(json.dumps(params_dict, indent=4, ensure_ascii=False))
    )
    api_parent_id = params_dict.get("api_parent_id")
    title = params_dict.get("title")
    vue_name = params_dict.get("vue_name")
    description = params_dict.get("description")
    icon = params_dict.get("icon")
    redirect = params_dict.get("redirect")
    menu_type = params_dict.get("menu_type")
    hidden = params_dict.get("hidden")
    permission_list = params_dict.get("permission")
    # permission传过来是个数组，需要变换成字符串
    permission_list = [str(x) for x in permission_list]
    permission = ":".join(permission_list)
    router_path = params_dict.get("router_path")
    component_path = params_dict.get("component_path")
    business_id = params_dict.get('business_id')

    try:
        if title:
            update_menu_dict = {
                "api_parent_id": api_parent_id,
                "title": title,
                'vue_name': vue_name,
                "description": description,
                "icon": icon,
                'redirect': redirect,
                "menu_type": menu_type,
                "hidden": hidden,
                "permission": permission,
                "router_path": router_path,
                "component_path": component_path,
                "business_id": business_id
            }
            # 更新一条菜单
            user_crud.update_menu(data=update_menu_dict)
            return restful.ok(message=update_menu_success)
    except:
        return restful.server_error(message=update_menu_failed)

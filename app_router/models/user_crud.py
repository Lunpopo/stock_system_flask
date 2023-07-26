import traceback

from gkestor_common_logger import Logger
from sqlalchemy import desc, asc, or_
from sqlalchemy.orm import aliased

from app_router.models.database import db
from app_router.models.base_models import AuthUser, AuthGroup, AuthApi, AuthFunction
from enums.enums import MenuEnum, MenuHiddenEnum
from exceptions.user_exception import *
from utils.authentication import pwd_context

logger = Logger()


def add_user(data):
    """
    添加用户信息
    :param data:
    :return:
    """
    try:
        data['password'] = pwd_context.hash(data['password'])
        user_obj = AuthUser(**data)
        db.session.add(user_obj)
        db.session.commit()
        db.session.flush()
        return user_obj
    except:
        db.session.rollback()
        raise AddUserException


def update_user(data):
    """
    更新用户信息
    :param data:
    :return:
    """
    try:
        data['password'] = pwd_context.hash(data['password'])

        auth_user_obj = AuthUser.query.filter_by(username=data['username']).first()
        auth_user_obj.group_id = data['group_id']
        if data.get('password'):
            auth_user_obj.password = data['password']
        if data.get('register_ip'):
            auth_user_obj.register_ip = data['register_ip']
        if data.get('status') is not None:
            auth_user_obj.status = data['status']
        db.session.commit()
        db.session.flush()

        return auth_user_obj
    except:
        db.session.rollback()
        raise UpdateUserException


def delete_user(username):
    """
    删除用户
    :param username:
    :return:
    """
    try:
        AuthUser.query.filter_by(username=username).delete()
        db.session.commit()
        db.session.flush()
    except:
        db.session.rollback()
        raise DeleteUserException


def get_user_by_name(username):
    """
    根据用户名查询是否有这条数据
    :param username: 用户名
    :return:
    """
    return AuthUser.query.filter_by(username=username).first()


def get_user_by_id(user_id):
    """
    根据 business_id 查询用户
    :param user_id: 用户id
    :return:
    """
    return AuthUser.query.filter_by(business_id=user_id).first()


def get_group_obj_by_user_id(user_id):
    """
    通过用户id获取对应的组名，例如99管理员组
    :param user_id: 用户id
    :return: group_name
    """
    A = aliased(AuthUser)
    B = aliased(AuthGroup)
    result_tuple_list = db.session.query(A, B).join(B, A.group_id == B.business_id).filter(
        A.business_id == user_id).first()
    return result_tuple_list[-1]


def get_group_by_name(group_name):
    """
    根据组名查询组的 business_id
    :param group_name: 组名
    :return:
    """
    return AuthGroup.query.filter_by(group_name=group_name).first()


def add_group(data):
    """
    添加用户信息
    :param data:
    :return:
    """
    try:
        group_obj = AuthGroup(**data)
        # group_obj.fill(data)
        db.session.add(group_obj)
        db.session.commit()
        db.session.flush()
        return group_obj.business_id
    except:
        db.session.rollback()
        raise AddGroupException


def delete_route(group_name):
    """
    根据 角色名（例如 editor） 删除关于这个角色的所有路由权限
    :param group_name: 例如：editor
    :return:
    """
    try:
        if group_name:
            # 删除所有的AuthApi中包含这个角色的权限
            auth_obj_list = AuthApi.query.all()

            for auth_obj in auth_obj_list:
                permission = auth_obj.permission
                permissions = permission.split(':')
                if group_name in permissions:
                    permissions.remove(group_name)
                    new_permission = ":".join(permissions)
                    # 更新
                    auth_obj.permission = new_permission
                    db.session.commit()
                    db.session.flush()
    except:
        db.session.rollback()
        raise DeleteRoleException


def delete_role_and_route(role_id, group_name):
    """
    根据 business_id 删除角色
    :param role_id: 角色id
    :param group_name: 角色名，例如：editor
    :return:
    """
    try:
        if role_id and group_name:
            AuthGroup.query.filter_by(business_id=role_id).delete()
            db.session.commit()
            db.session.flush()

            # 删除所有的AuthApi中包含这个角色的权限
            delete_route(group_name=group_name)
    except:
        db.session.rollback()
        raise DeleteRoleAndRouteException


def update_role_and_route(group_dict, routes):
    """
    更新角色和所属路由权限
    :param group_dict:
    :param routes: 路由dict
    :return:
    """
    try:
        auth_group_obj = AuthGroup.query.filter_by(business_id=group_dict['business_id']).first()
        if group_dict.get('group_name'):
            auth_group_obj.group_name = group_dict['group_name']
        if group_dict.get('group_label'):
            auth_group_obj.group_label = group_dict['group_label']
        if group_dict.get('description'):
            auth_group_obj.description = group_dict['description']
        db.session.commit()
        db.session.flush()

        # 先删除所有的有关这个角色的路由权限（后面再追加）
        delete_route(group_name=group_dict['group_name'])
        # 更新路由
        add_routes_role(group_name=group_dict['group_name'], routes=routes)

        return auth_group_obj
    except:
        db.session.rollback()
        raise UpdateRoleAndRouteException


def add_routes_role(group_name, routes):
    """
    添加角色权限到路由中去
    :param group_name:
    :param routes:
    :return:
    """
    for route_obj in routes:
        # 先玩父级的
        if route_obj.get('name') and route_obj.get('path'):
            # 先查询这条 AuthApi 数据
            auth_obj = AuthApi.query.filter_by(router_path=route_obj['path'], vue_name=route_obj['name']).first()
            old_permission = auth_obj.permission
            old_permissions = old_permission.split(':')
            # 如果老的权限里面没有，就进行追加
            if group_name not in old_permissions:
                new_permission = "{}:{}".format(old_permission, group_name)
                # 更新 permission
                auth_obj.query.filter_by(router_path=route_obj['path'], vue_name=route_obj['name']).update(
                    {'permission': new_permission})
                db.session.commit()
                db.session.flush()

        if route_obj.get('children'):
            children_routes_list = route_obj.get('children')
            # 递归
            add_routes_role(group_name, children_routes_list)


def add_role_and_route(group_dict, routes):
    """
    新增角色和新增关于这个角色的所有路由权限
    :param group_dict:
    :param routes: 路由dict
    :return:
    """
    try:
        # 先增加 AuthGroup 数据
        group_obj = AuthGroup(**group_dict)
        # group_obj.fill(data)
        db.session.add(group_obj)
        db.session.commit()
        db.session.flush()

        # 增加上一条新增的 role 到这些路由中去
        add_routes_role(group_dict['group_name'], routes)
        return group_obj
    except:
        db.session.rollback()
        raise AddRoleAndRouteException


def add_menu(data):
    """
    添加一条菜单（api）
    :param data:
    :return:
    """
    try:
        menu_obj = AuthApi(**data)
        # group_obj.fill(data)
        db.session.add(menu_obj)
        db.session.commit()
        db.session.flush()
        return menu_obj.title
    except:
        db.session.rollback()
        raise AddMenuException


def add_api(data):
    """
    添加一条功能（api）
    :param data:
    :return:
    """
    try:
        api_obj = AuthFunction(**data)
        db.session.add(api_obj)
        db.session.commit()
        db.session.flush()
        return api_obj.title
    except:
        db.session.rollback()
        raise AddApiException


def update_api(data):
    """
    更新一条功能（api）
    :param data:
    :return:
    """
    business_id = data.get('business_id')
    try:
        # 根据业务id查询这条数据
        api_obj = get_auth_function_by_id(business_id=business_id)
        if api_obj:
            # 执行更新操作
            api_obj.query.filter_by(business_id=business_id).update(data)
            db.session.commit()
    except:
        logger.info(traceback.format_exc())
        db.session.rollback()
        raise UpdateApiException


def update_menu(data):
    """
    更新一条菜单（api）
    :param data:
    :return:
    """
    business_id = data.get('business_id')
    try:
        # 根据业务id查询这条数据
        api_obj = get_auth_api_by_id(business_id=business_id)
        if api_obj:
            # 执行更新操作
            api_obj.query.filter_by(business_id=business_id).update(data)
            db.session.commit()
    except:
        db.session.rollback()
        raise UpdateMenuException


def get_all_permission():
    """
    获取所有的api权限
    :return:
    """
    all_group_list = AuthGroup.query.all()
    return [_.as_dict() for _ in all_group_list]


def get_parent_menu():
    """
    获取非最后一级的菜单
    :return:
    """
    return AuthApi.query.filter(AuthApi.menu_type == 0).order_by(desc('update_time')).all()


def get_auth_api_by_id(business_id):
    """
    通过 auth_api的business_id 查找这条数据
    :param business_id: 这条数据的业务id
    :return:
    """
    return AuthApi.query.filter_by(business_id=business_id).first()


def get_auth_function_by_id(business_id):
    """
    通过 auth_function 的 business_id 查找这条数据
    :param business_id: 这条数据的业务id
    :return:
    """
    return AuthFunction.query.filter_by(business_id=business_id).first()


def get_menu(page, limit):
    """
    获取菜单列表
    :param page:
    :param limit:
    :return:
    """
    result_list = AuthApi.query.order_by(desc('update_time')).offset(page).limit(limit).all()
    auth_api_list = []
    for auth_api_obj in result_list:
        menu_type = auth_api_obj.menu_type
        hidden = auth_api_obj.hidden
        permission = auth_api_obj.permission
        auth_api_dict = auth_api_obj.as_dict()

        # 用作前端显示的展示
        # 菜单等级
        auth_api_dict['menu_type_label'] = MenuEnum(menu_type).name
        # 父级菜单
        parent_id = auth_api_obj.api_parent_id
        if parent_id:
            this_auth_obj = get_auth_api_by_id(parent_id)
            auth_api_dict['api_parent_id_label'] = this_auth_obj.title
        # 菜单是否隐藏
        auth_api_dict['hidden_label'] = MenuHiddenEnum(hidden).name
        # 展示菜单的权限
        if ":" in permission:
            permissions = permission.split(":")
            auth_api_dict['permission'] = permissions
        else:
            auth_api_dict['permission'] = [permission]

        auth_api_list.append(auth_api_dict)

    return {
        "data": auth_api_list,
        "count": AuthApi.query.count()
    }


def get_api(page, limit):
    """
    获取功能api列表
    :param page:
    :param limit:
    :return:
    """
    result_list = AuthFunction.query.order_by(desc('update_time')).offset(page).limit(limit).all()
    return_api_list = []
    for auth_api_obj in result_list:
        permission = auth_api_obj.permission
        auth_api_dict = auth_api_obj.as_dict()

        # 用作前端显示的展示
        # 展示菜单的权限
        if ":" in permission:
            permissions = permission.split(":")
            auth_api_dict['permission'] = permissions
        else:
            auth_api_dict['permission'] = [permission]

        return_api_list.append(auth_api_dict)

    return {
        "data": return_api_list,
        "count": AuthFunction.query.count()
    }


def search_api(title, page, limit):
    """
    搜搜api功能
    :param title: api名字
    :param page:
    :param limit:
    :return:
    """
    if title:
        # 多个模糊查询一起
        result_list = AuthFunction.query.filter(or_(
            AuthFunction.title.like('%{}%'.format(title)), AuthFunction.api_name.like('%{}%'.format(title))
        )).order_by(desc('update_time')).offset(page).limit(limit).all()
    else:
        result_list = AuthFunction.query.order_by(desc('update_time')).offset(page).limit(limit).all()

    return_api_list = []
    for auth_api_obj in result_list:
        permission = auth_api_obj.permission
        auth_api_dict = auth_api_obj.as_dict()

        # 用作前端显示的展示
        # 展示菜单的权限
        if ":" in permission:
            permissions = permission.split(":")
            auth_api_dict['permission'] = permissions
        else:
            auth_api_dict['permission'] = [permission]

        return_api_list.append(auth_api_dict)

    if title:
        return {
            "data": return_api_list,
            "count": AuthFunction.query.filter(or_(
                AuthFunction.title.like('%{}%'.format(title)), AuthFunction.api_name.like('%{}%'.format(title))
            )).count()
        }
    else:
        return {
            "data": return_api_list,
            "count": AuthFunction.query.count()
        }


def get_all_role():
    """
    获取所有的角色
    :return:
    """
    return AuthGroup.query.order_by(asc('create_time')).all()


def get_all_menu():
    """
    获取所有的菜单列表
    :return: 所有的 api 路由列表
    """
    return AuthApi.query.order_by(asc('create_time')).all()


def delete_menu_by_id(business_id):
    """
    通过业务id删除菜单
    :param business_id:
    :return:
    """
    try:
        # 如果要删除的是一级菜单，那要把下面的所有的菜单全部删除
        auth_api_obj = AuthApi.query.filter_by(business_id=business_id).first()
        if auth_api_obj.menu_type == 0:
            # 一级菜单
            AuthApi.query.filter_by(api_parent_id=auth_api_obj.business_id).delete()
            db.session.commit()
        AuthApi.query.filter_by(business_id=business_id).delete()
        db.session.commit()
    except:
        db.session.rollback()
        raise DeleteMenuException


def delete_api_by_id(business_id):
    """
    通过业务id删除功能api
    :param business_id:
    :return:
    """
    try:
        AuthFunction.query.filter_by(business_id=business_id).delete()
        db.session.commit()
    except:
        db.session.rollback()
        raise DeleteApiException

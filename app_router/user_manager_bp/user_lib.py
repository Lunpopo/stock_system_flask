import requests

from app_router.models.base_models import AuthUser, AuthApi
from utils.authentication import verify_password


def check_user(username, password):
    """
    检查用户名和密码
    :param username:
    :param password:
    :return:
    """
    user = AuthUser.query.filter_by(username=username).first()
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


def get_current_ip():
    """
    获取当前ip
    :return:
    """
    res = requests.get('http://myip.ipip.net', timeout=5)
    return res.text.split("：")[1].split(" ")[0]


def filter_routes_by_role(all_routes_list, current_role):
    """
    根据角色过滤没有权限的路由
    :param all_routes_list: 所有的路由列表（dict类型）
    :param current_role: 当前角色
    :return: 返回过滤之后的路由list
    """
    if current_role == 'admin':
        return all_routes_list

    return_routes_list = []
    for routes_obj in all_routes_list:
        routes_parent_dict = {}
        children_routes_list = []
        # 这里只会有所有的一级目录
        if routes_obj.get('meta'):
            if current_role in routes_obj['meta']['roles']:
                routes_parent_dict = routes_obj
            else:
                pass
        else:
            # 如果没有meta下面的roles的话，那么就是所有权限都可以进去
            routes_parent_dict = routes_obj

        if routes_parent_dict and routes_parent_dict.get('children'):
            for children_routes in routes_parent_dict.get('children'):
                # 如果下面有二级目录
                if children_routes.get('meta'):
                    if current_role in children_routes['meta']['roles']:
                        children_routes_list.append(children_routes)
                    else:
                        pass
                else:
                    # 如果没有meta下面的roles的话，那么就是所有权限都可以进去
                    children_routes_list.append(children_routes)

        # 有可能出现一级目录有权限，下面的某些二级目录没有权限的情况
        if children_routes_list:
            routes_parent_dict['children'] = children_routes_list
        if routes_parent_dict:
            return_routes_list.append(routes_parent_dict)

    return return_routes_list


def generate_routes(all_menu_query_list):
    """
    生成vue前端可用的动态路由dict
    :param all_menu_query_list: 从数据库中查询到的所有的菜单列表（包含一级和二级所有的菜单）是个 AuthApi 对象
    :return: 路由list
    """
    auth_api_list = []
    for auth_api_obj in all_menu_query_list:
        api_parent_id = auth_api_obj.api_parent_id
        menu_type = auth_api_obj.menu_type
        if api_parent_id is None and menu_type == 0:
            # 一级菜单
            permission = auth_api_obj.permission
            router_path = auth_api_obj.router_path

            # 展示菜单的权限，用, 隔开
            if ":" in permission:
                permissions = permission.split(":")
                # permissions_label = [UserGroupEnum(int(x)).name for x in permissions]
            else:
                permissions = permission
                # permissions_label = [UserGroupEnum(int(permission)).name]
            _dict = {
                "path": router_path,
                'component': auth_api_obj.component_path,
                'alwaysShow': True,
                'meta': {
                    'roles': permissions
                }
            }

            hidden = auth_api_obj.hidden
            redirect = auth_api_obj.redirect
            name = auth_api_obj.vue_name
            title = auth_api_obj.title
            icon = auth_api_obj.icon
            if hidden:
                _dict['hidden'] = hidden
            if redirect:
                _dict['redirect'] = redirect
            if name:
                _dict['name'] = name
            if title:
                _dict['meta']['title'] = title
            if icon:
                _dict['meta']['icon'] = icon

            # 找所有的一级目录，然后再找他们各自的所有的子目录
            children_api_list = AuthApi.query.filter_by(api_parent_id=auth_api_obj.business_id).all()
            children_obj_list = []
            for children_api_obj in children_api_list:
                children_permission = children_api_obj.permission
                children_router_path = children_api_obj.router_path
                # 去除 二级目录 下 router_path 的/（一级目录不用去除）
                children_router_path = children_router_path.split('/')[-1]
                # 展示菜单的权限，用, 隔开
                if ":" in children_permission:
                    children_permission = children_permission.split(":")
                else:
                    children_permission = children_permission
                children_api_dict = {
                    "path": children_router_path,
                    'component': children_api_obj.component_path,
                    'meta': {
                        'roles': children_permission
                    }
                }
                children_name = children_api_obj.vue_name
                children_title = children_api_obj.title
                children_icon = children_api_obj.icon
                children_hidden = children_api_obj.hidden
                if children_name:
                    children_api_dict['name'] = children_name
                if children_title:
                    children_api_dict['meta']['title'] = children_title
                if children_icon:
                    children_api_dict['meta']['icon'] = children_icon
                if children_hidden:
                    children_api_dict['hidden'] = children_hidden
                children_obj_list.append(children_api_dict)

            _dict['children'] = children_obj_list
            auth_api_list.append(_dict)

    # 最后需要加上 404 路由
    auth_api_list.append({'path': '*', 'redirect': '/404', 'hidden': True})
    return auth_api_list

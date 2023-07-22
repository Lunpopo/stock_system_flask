"""
用户模块的自定义异常类集合
"""
from messages.messages import *


class AddUserException(Exception):
    """
    添加用户自定义异常
    """
    def __init__(self, msg=add_user_failed):
        self.msg = msg

    def __str__(self):
        return self.msg


class DeleteUserException(Exception):
    """
    删除用户自定义异常
    """
    def __init__(self, msg=delete_user_failed):
        self.msg = msg

    def __str__(self):
        return self.msg


class AddGroupException(Exception):
    """
    添加角色自定义异常
    """
    def __init__(self, msg=add_role_failed):
        self.msg = msg

    def __str__(self):
        return self.msg


class DeleteRoleException(Exception):
    """
    删除关于这个角色的所有路由权限异常
    """
    def __init__(self, msg=delete_role_routes_failed):
        self.msg = msg

    def __str__(self):
        return self.msg


class DeleteRoleAndRouteException(Exception):
    """
    删除角色和删除关于这个角色的所有路由权限异常
    """
    def __init__(self, msg=delete_role_and_routes_failed):
        self.msg = msg

    def __str__(self):
        return self.msg


class UpdateRoleAndRouteException(Exception):
    """
    更新角色和更新关于这个角色的所有路由权限异常
    """
    def __init__(self, msg=update_role_and_routes_failed):
        self.msg = msg

    def __str__(self):
        return self.msg


class AddRoleAndRouteException(Exception):
    """
    新增角色和新增关于这个角色的所有路由权限异常
    """
    def __init__(self, msg=add_role_and_routes_failed):
        self.msg = msg

    def __str__(self):
        return self.msg


class AddMenuException(Exception):
    """
    新增菜单（api）异常
    """
    def __init__(self, msg=add_menu_failed):
        self.msg = msg

    def __str__(self):
        return self.msg


class UpdateMenuException(Exception):
    """
    更新菜单（api）异常
    """
    def __init__(self, msg=update_menu_failed):
        self.msg = msg

    def __str__(self):
        return self.msg


class DeleteMenuException(Exception):
    """
    删除菜单（api）异常
    """
    def __init__(self, msg=delete_menu_failed):
        self.msg = msg

    def __str__(self):
        return self.msg
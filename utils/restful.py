#!/usr/bin/env python
# encoding: utf8
# @Author  ：xie.yx
# @Date    ：2022/3/23 13:42
# encoding: utf8
import time

from flask import Response, json


class HttpCode(object):
    ok = 200
    paramserror = 400
    # 无权限访问页面（或者功能）
    unauth = 401
    methoderror = 405
    servererror = 500
    # token过期
    token_expired = 50014
    # 非法登录
    illegal_token = 50008
    # 拒绝访问
    forbidden = 403


def result(status=HttpCode.ok, code=20000, message="", data=None, succ=True, kwargs=None):
    json_dict = {"code": code, "msg": message, "data": data, "succ": succ, "ts": int(time.time() * 1000)}

    if kwargs and isinstance(kwargs, dict) and kwargs.keys():
        json_dict.update(kwargs)

    # return Response(status_code=code, content=json_dict)
    return Response(json.dumps(json_dict), content_type='application/json', status=status)


# 正常返回
def ok(message='', data=None):
    return result(code=20000, message=message, data=data)


# 参数错误
def params_error(message="", data=None):
    return result(status=HttpCode.paramserror, code=HttpCode.paramserror, message=message, data=data, succ=False)


# 未授权错误
def unauth(message="您没有权限访问此功能", data=None):
    return result(status=HttpCode.unauth, code=HttpCode.unauth, message=message, data=data, succ=False)


# 方法错误
def method_error(message="", data=None):
    return result(status=HttpCode.methoderror, code=HttpCode.methoderror, message=message, data=data, succ=False)


# 服务器错误
def server_error(message="", data=None):
    return result(status=HttpCode.servererror, code=HttpCode.servererror, message=message, data=data, succ=False)


# token过期
def token_expired(message="您的登录信息已过期！", data=None):
    return result(code=HttpCode.token_expired, message=message, data=data, succ=False)


# 非法token
def illegal_token(message="非法登录！", data=None):
    return result(status=HttpCode.forbidden, code=HttpCode.illegal_token, message=message, data=data, succ=False)

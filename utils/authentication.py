from datetime import datetime, timedelta
from typing import Any, Union

import jose
from gkestor_common_logger import Logger
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import aliased

from app_router.models.database import db
from app_router.models.base_models import AuthUser, AuthGroup, AuthFunction
from configs.contents import ACCESS_TOKEN_EXPIRE_MINUTES, AUTH_SECRET_KEY, ALGORITHM
from enums.enums import AuthStatusEnum

logger = Logger()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password):
    """
    使用的算法是Bcrypt
    哈希来自用户的密码
    :param password: 原密码
    :return: 哈希后的密码
    """
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    """
    校验接收的密码是否与存储的哈希值匹配
    :param plain_password: 原密码
    :param hashed_password: 哈希后的密码
    :return: 返回值为bool类型，校验成功返回True,反之False
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    """
    创建token，例如：create_access_token(user.business_id, expires_delta=access_token_expires)
    :param subject:
    :param expires_delta:
    :return:
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    # 添加失效时间：exp
    to_encode = {"exp": expire, "sub": str(subject)}
    # SECRET_KEY：密钥
    # ALGORITHM：JWT令牌签名算法
    encoded_jwt = jwt.encode(to_encode, AUTH_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token):
    """
    解码token
    :param token:
    :return:
    """
    return jwt.decode(token, AUTH_SECRET_KEY, algorithms='ALGORITHM', options={"verify_signature": False})


def auth_check(user_token, api):
    """
    检查用户是否登录过期装饰器
    :param user_token: 前端获取的 token
    :param api: api的路径（完整的路径），例如：data_display/get_product_data
    :return:
    """
    try:
        # 与数据库中该路由的权限进行匹配，如果不匹配那就返回false，如果匹配那就走人
        if api.endswith('/'):
            api = api[:-1]
        if api.startswith('/'):
            api = api[1:]

        if user_token:
            user_token = user_token.split("Bearer:")[-1]
            decode_token_dict = decode_token(user_token)
            user_id = decode_token_dict.get("sub")

            A = aliased(AuthUser)
            B = aliased(AuthGroup)
            result_tuple_list = db.session.query(A, B).join(B, A.group_id == B.business_id).filter(
                A.business_id == user_id).first()
            group_obj = result_tuple_list[-1]

            # 当前登录的角色
            current_role = group_obj.group_name

            # 查询api功能表是否有这条api
            match_obj = AuthFunction.query.filter(AuthFunction.api_name.like('%{}%'.format(api))).first()
            if match_obj:
                # 对权限进行匹配
                permission = match_obj.permission
                permissions = permission.split(":")
                if current_role in permissions:
                    return AuthStatusEnum.ok.value
                else:
                    return AuthStatusEnum.unauth.value
            else:
                return AuthStatusEnum.unauth.value
        else:
            # 没有Token，
            return AuthStatusEnum.illegal_token.value
    except jose.exceptions.ExpiredSignatureError:
        # 权限过期
        return AuthStatusEnum.expire.value
    except:
        # 未知错误
        return AuthStatusEnum.unauth.value

from datetime import datetime, timedelta
from typing import Any, Union

from jose import jwt
from passlib.context import CryptContext

from configs.contents import ACCESS_TOKEN_EXPIRE_MINUTES, AUTH_SECRET_KEY, ALGORITHM

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
"""
用户模块的自定义异常类集合
"""
from messages.messages import *


class AddProductException(Exception):
    """
    添加产品异常
    """
    def __init__(self, msg=add_product_failed):
        self.msg = msg

    def __str__(self):
        return self.msg


class AddDealerProductException(Exception):
    """
    添加经销商产品异常
    """
    def __init__(self, msg=add_dealer_product_failed):
        self.msg = msg

    def __str__(self):
        return self.msg


class AddDealerNameException(Exception):
    """
    添加一个经销商名单异常
    """
    def __init__(self, msg=add_dealer_name_failed):
        self.msg = msg

    def __str__(self):
        return self.msg


class UpdateProductException(Exception):
    """
    更新产品异常
    """
    def __init__(self, msg=update_product_failed):
        self.msg = msg

    def __str__(self):
        return self.msg


class UpdateDealerProductException(Exception):
    """
    更新经销商产品异常
    """
    def __init__(self, msg=update_dealer_product_failed):
        self.msg = msg

    def __str__(self):
        return self.msg


class UpdateDealerNameException(Exception):
    """
    更新 经销商名单 异常
    """
    def __init__(self, msg=update_dealer_name_failed):
        self.msg = msg

    def __str__(self):
        return self.msg


class DeleteProductException(Exception):
    """
    删除产品异常
    """
    def __init__(self, msg=delete_product_failed):
        self.msg = msg

    def __str__(self):
        return self.msg


class DeleteDealerProductException(Exception):
    """
    删除经销商产品异常
    """
    def __init__(self, msg=delete_dealer_product_failed):
        self.msg = msg

    def __str__(self):
        return self.msg


class DeleteDealerNameException(Exception):
    """
    删除 经销商列表名单 异常
    """
    def __init__(self, msg=delete_dealer_name_failed):
        self.msg = msg

    def __str__(self):
        return self.msg



class MultiDeleteProductException(Exception):
    """
    批量删除产品异常
    """
    def __init__(self, msg=multiply_delete_product_failed):
        self.msg = msg

    def __str__(self):
        return self.msg


class MultiDeleteDealerProductException(Exception):
    """
    批量删除经销商产品异常
    """
    def __init__(self, msg=multiply_delete_dealer_product_failed):
        self.msg = msg

    def __str__(self):
        return self.msg

"""
出入库订单模块的自定义异常类集合
"""
from messages.messages import *


class AddStockListException(Exception):
    """
    新增股票交易信息列表出错
    """

    def __init__(self, msg=add_stock_list_failed):
        self.msg = msg

    def __str__(self):
        return self.msg


class DelStockException(Exception):
    """
    删除股票及其交易信息出错
    """

    def __init__(self, msg=del_stock_failed):
        self.msg = msg

    def __str__(self):
        return self.msg


class UpdateStockTransactionException(Exception):
    """
    更新股票和股票交易信息列表出错
    """

    def __init__(self, msg=update_stock_transaction_failed):
        self.msg = msg

    def __str__(self):
        return self.msg


class UpdateStockListException(Exception):
    """
    更新 股票列表 自定义异常
    """

    def __init__(self, msg=update_stock_list_failed):
        self.msg = msg

    def __str__(self):
        return self.msg


class UpdateTransactinoException(Exception):
    """
    更新 股票交易信息 自定义异常
    """

    def __init__(self, msg=update_transaction_info_failed):
        self.msg = msg

    def __str__(self):
        return self.msg


class TransactinoNotExist(Exception):
    """
    该条股票交易信息不存在
    """

    def __init__(self, msg=transaction_info_not_exist):
        self.msg = msg

    def __str__(self):
        return self.msg


class DeleteTransactionException(Exception):
    """
    删除股票交易列表自定义异常
    """

    def __init__(self, msg=del_transaction_failed):
        self.msg = msg

    def __str__(self):
        return self.msg

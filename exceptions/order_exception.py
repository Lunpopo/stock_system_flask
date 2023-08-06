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


class AddOutboundException(Exception):
    """
    新增出库单自定义异常
    """

    def __init__(self, msg=add_outbound_order_failed):
        self.msg = msg

    def __str__(self):
        return self.msg


class UpdateOutboundException(Exception):
    """
    更新出库单自定义异常
    """

    def __init__(self, msg=update_outbound_order_failed):
        self.msg = msg

    def __str__(self):
        return self.msg


class UpdatePurchaseException(Exception):
    """
    更新入库单自定义异常
    """

    def __init__(self, msg=update_purchase_order_failed):
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


class DeletePurchaseException(Exception):
    """
    删除入库单自定义异常
    """

    def __init__(self, msg=del_purchase_order_failed):
        self.msg = msg

    def __str__(self):
        return self.msg


class DeleteOutboundException(Exception):
    """
    删除出库单自定义异常
    """

    def __init__(self, msg=del_outbound_order_failed):
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


class DeletePurchaseProductListException(Exception):
    """
    删除入库单的所有产品自定义异常
    """

    def __init__(self, msg=del_purchase_product_list_order_failed):
        self.msg = msg

    def __str__(self):
        return self.msg


class DeleteOutboundProductListException(Exception):
    """
    删除出库单的所有产品自定义异常
    """

    def __init__(self, msg=del_outbound_product_list_order_failed):
        self.msg = msg

    def __str__(self):
        return self.msg


class AddPurchaseProductException(Exception):
    """
    新增入库单产品自定义异常
    """

    def __init__(self, msg=add_purchase_order_product_failed):
        self.msg = msg

    def __str__(self):
        return self.msg


class AddOutboundProductException(Exception):
    """
    新增出库单产品自定义异常
    """

    def __init__(self, msg=add_outbound_order_product_failed):
        self.msg = msg

    def __str__(self):
        return self.msg

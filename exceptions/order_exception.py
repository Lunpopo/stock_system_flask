"""
出入库订单模块的自定义异常类集合
"""
from messages.messages import *


class AddPurchaseException(Exception):
    """
    新增入库单自定义异常
    """

    def __init__(self, msg=add_purchase_order_failed):
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

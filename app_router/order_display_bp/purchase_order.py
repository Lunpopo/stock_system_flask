import json

from flask import Blueprint, request
from gkestor_common_logger import Logger

from app_router.models import order_crud
from enums.enums import AuthCheckEnum
from messages.messages import *
from utils import restful
from utils.authentication import auth_check
from utils.date_utils import time_to_timestamp

purchase_order_bp = Blueprint("purchase_order", __name__, url_prefix="/purchase_order")
logger = Logger()


# DONE
@purchase_order_bp.route("/get_stock_info_by_id", methods=["POST"])
def get_stock_info_by_id():
    """
    通过 stock id 获取股票信息
    :return:
    """
    auth_status = auth_check(user_token=request.headers.get('Authorization'),
                             api='purchase_order/get_purchase_product_details')
    if AuthCheckEnum[auth_status].value is not True:
        return AuthCheckEnum[auth_status].value

    data = request.get_data(as_text=True)
    params_dict = json.loads(data)
    # 入库订单ID
    stock_id = params_dict.get("stock_id")

    params_dict = {"stock_id": stock_id}
    logger.info("/get_purchase_product_details 前端的入参参数：\n{}".format(
        json.dumps(params_dict, indent=4, ensure_ascii=False))
    )

    # 获取股票信息
    result = order_crud.get_stock_info_by_id(data_id=stock_id)
    # 该入库订单下的所有产品
    stock_obj = result.get("stock_obj")
    stock_obj = stock_obj.as_dict()
    stock_obj = time_to_timestamp([stock_obj])[0]
    transaction_obj_list = result.get("transaction_obj_list")
    transaction_obj_list = [_.as_dict() for _ in transaction_obj_list]
    transaction_obj_list = time_to_timestamp(transaction_obj_list)
    return_data = {
        "Success": True,
        "code": 2000,
        "msg": "",
        "count": result.get('count'),
        "stock_obj": stock_obj,
        "transaction_obj_list": transaction_obj_list
    }
    return restful.ok(message="返回产品列表数据", data=return_data)


# DOING
@purchase_order_bp.route("/get_stock_transaction_by_id", methods=["POST"])
def get_stock_transaction_by_id():
    """
    通过 stock id 获取股票和详细的交易信息（例如产生的盈利和交易状态）
    :return:
    """
    auth_status = auth_check(user_token=request.headers.get('Authorization'),
                             api='purchase_order/get_purchase_product_details')
    if AuthCheckEnum[auth_status].value is not True:
        return AuthCheckEnum[auth_status].value

    data = request.get_data(as_text=True)
    params_dict = json.loads(data)
    # 入库订单ID
    stock_id = params_dict.get("stock_id")

    params_dict = {"stock_id": stock_id}
    logger.info("/get_purchase_product_details 前端的入参参数：\n{}".format(
        json.dumps(params_dict, indent=4, ensure_ascii=False))
    )

    # 获取股票信息
    result = order_crud.get_stock_info_by_id(data_id=stock_id)
    # 该入库订单下的所有产品
    stock_obj = result.get("stock_obj")
    stock_obj = stock_obj.as_dict()
    stock_obj = time_to_timestamp([stock_obj])[0]

    # 该股票的交易列表
    transaction_obj_list = result.get("transaction_obj_list")
    transaction_obj_list = [_.as_dict() for _ in transaction_obj_list]
    transaction_obj_list = time_to_timestamp(transaction_obj_list)

    # 保存交易状态不为清仓的情况
    save_list = []
    for index, transaction_obj in enumerate(transaction_obj_list):
        transaction_obj['stock_name'] = stock_obj['stock_name']
        if not transaction_obj['transaction_status']:
            save_list.append(transaction_obj)

    # 专门处理不为清仓的状态
    for index, transaction_obj in enumerate(save_list):
        if index == 0:
            transaction_obj['remain_positions'] = transaction_obj['quantity']
            transaction_obj['cost'] = transaction_obj['buy_price']
            break

        # 不为首个买入的状态
        if transaction_obj['transaction_type'] == '买入':
            # 此次买入的价格
            current_buy_price = transaction_obj['buy_price']
            # 此次买入的数量
            current_buy_quantity = transaction_obj['quantity']
            # 上一条交易的成本价格
            previous_buy_price = save_list[index - 1]['cost']
            # 上一条交易的剩余仓位
            previous_remain_quantity = save_list[index - 1]['remain_positions']

            # 计算此次的买入成本：(当前买入价格 x 当前买入的数量 + 上一条计算好的成本价格 * 上一条计算好的剩余仓位) / (当前买入的数量 + 上一条计算好的剩余数量)
            current_buy_cost = (
                                           current_buy_price * current_buy_quantity + previous_buy_price * previous_remain_quantity) / (
                                           current_buy_quantity + previous_remain_quantity)
            # 计算此次的剩余数量（当前买入的数量 + 上一条计算好的剩余数量）
            current_remain_quantity = current_buy_quantity + previous_remain_quantity

    return_data = {
        "Success": True,
        "code": 2000,
        "msg": "",
        "count": result.get('count'),
        "data": transaction_obj_list
    }

    return restful.ok(message="返回产品列表数据", data=return_data)


# DONE 完成
@purchase_order_bp.route("/get_stock_list", methods=["GET"])
def get_stock_list():
    """
    获取入库单列表
    :return:
    """
    auth_status = auth_check(user_token=request.headers.get('Authorization'), api='purchase_order/get_purchase_order')
    if AuthCheckEnum[auth_status].value is not True:
        return AuthCheckEnum[auth_status].value

    page = int(request.args.get("page"))
    limit = int(request.args.get("limit"))

    params_dict = {"page": page, "limit": limit}
    logger.info("/get_stock_list 前端的入参参数：\n{}".format(json.dumps(params_dict, indent=4, ensure_ascii=False)))

    # 前端page从1开始
    page -= 1
    page = page * limit
    result = order_crud.get_stock_list_limit(page=page, limit=limit)
    result_data = result.get("data")
    data_list = []
    for _ in result_data:
        _dict = _.as_dict()
        data_list.append(_dict)

    # 增加一个产品采购单的种类
    for stock_list_obj in data_list:
        stock_business_id = stock_list_obj['business_id']
        transaction_result_list = order_crud.get_transaction_by_stock_id(data_id=stock_business_id)
        transaction_obj_list = transaction_result_list.get("data")
        stock_list_obj['transaction_count'] = transaction_result_list.get("count")  # 交易次数

        # 计算买入和卖出的总额度
        buy_price_count = 0.0
        sell_price_count = 0.0
        for transaction_obj in transaction_obj_list:
            if transaction_obj.transaction_type == '买入':
                buy_price_count += transaction_obj.subtotal_price
            else:
                sell_price_count += transaction_obj.subtotal_price
        stock_list_obj['buy_price_count'] = buy_price_count
        stock_list_obj['sell_price_count'] = sell_price_count

    # 统一转换成时间戳的形式
    data_list = time_to_timestamp(data_list)

    return_data = {
        "Success": True,
        "code": 2000,
        "msg": "",
        "count": result.get('count'),
        "data": data_list
    }
    return restful.ok(message="返回进货单列表数据", data=return_data)


# DONE 完成
@purchase_order_bp.route("/add_stock_list", methods=["POST"])
def add_stock_list():
    """
    获取入库单列表
    :return:
    """
    auth_status = auth_check(user_token=request.headers.get('Authorization'), api='purchase_order/get_purchase_order')
    if AuthCheckEnum[auth_status].value is not True:
        return AuthCheckEnum[auth_status].value

    data = request.get_data(as_text=True)
    params_dict = json.loads(data)
    logger.info(
        "/add_purchase_order 前端传入的参数为：\n{}".format(json.dumps(params_dict, indent=4, ensure_ascii=False))
    )

    stock_name = params_dict.get("stock_name")
    stock_code = params_dict.get("stock_code")
    stock_transaction_list = params_dict.get('stock_transaction_list')
    remarks = params_dict.get("remarks")
    stock_list_dict = {
        "stock_name": stock_name,
        "stock_code": stock_code,
        "remarks": remarks
    }

    order_crud.add_stock_list(stock_list_data=stock_list_dict, stock_transaction_list_data=stock_transaction_list)

    return restful.ok(message="返回进货单列表数据", data=params_dict)


# DONE 完成
@purchase_order_bp.route("/update_stock_list", methods=["POST"])
def update_stock_list():
    """
    更新股票列表和该股票的交易列表
    :return:
    """
    auth_status = auth_check(user_token=request.headers.get('Authorization'), api='purchase_order/get_purchase_order')
    if AuthCheckEnum[auth_status].value is not True:
        return AuthCheckEnum[auth_status].value

    data = request.get_data(as_text=True)
    params_dict = json.loads(data)
    logger.info(
        "/update_stock_list 前端传入的参数为：\n{}".format(json.dumps(params_dict, indent=4, ensure_ascii=False))
    )

    stock_name = params_dict.get("stock_name")
    stock_code = params_dict.get("stock_code")
    transaction_list = params_dict.get("stock_transaction_list")
    remarks = params_dict.get("remarks")
    stock_id = params_dict.get("business_id")

    if transaction_list:
        stock_dict = {
            "stock_name": stock_name,
            "stock_code": stock_code,
            "business_id": stock_id,
            "remarks": remarks
        }

        order_crud.update_stock_transaction_list(stock_dict, transaction_list)
        return restful.ok(message=update_stock_transaction_success)
    return restful.server_error(message=update_purchase_order_not_zero)


@purchase_order_bp.route("/del_purchase_order", methods=["POST"])
def del_purchase_order():
    """
    根据 订单ID 删除一条入库单
    :return:
    """
    auth_status = auth_check(user_token=request.headers.get('Authorization'), api='purchase_order/del_purchase_order')
    if AuthCheckEnum[auth_status].value is not True:
        return AuthCheckEnum[auth_status].value

    data = request.get_data(as_text=True)
    params_dict = json.loads(data)
    logger.info("/del_purchase_order 前端传入的参数为：\n{}".format(json.dumps(params_dict, indent=4, ensure_ascii=False)))

    business_id = params_dict.get("purchase_order_id")
    try:
        order_crud.del_purchase_order_by_id(data_id=business_id)
    except:
        return restful.server_error(message=del_purchase_order_failed)

    return restful.ok(message=del_purchase_order_success)

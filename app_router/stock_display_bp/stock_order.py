import json

from flask import Blueprint, request
from gkestor_common_logger import Logger

from app_router.models import order_crud
from enums.enums import AuthCheckEnum
from messages.messages import *
from utils import restful
from utils.authentication import auth_check
from utils.date_utils import time_to_timestamp

stock_bp = Blueprint("stock", __name__, url_prefix="/purchase_order")
logger = Logger()


@stock_bp.route("/get_stock_info_by_id", methods=["POST"])
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


@stock_bp.route("/get_stock_transaction_by_id", methods=["POST"])
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

    # 获取该股票的交易列表
    before_update_result = order_crud.get_stock_info_by_id(data_id=stock_id)  # 未更新数据前的查询结果
    transaction_obj_list = before_update_result.get("transaction_obj_list")
    transaction_obj_list = [_.as_dict() for _ in transaction_obj_list]

    def _update_latest_transaction(_stock_id, _obj_list):
        """
        更新最新的交易列表状态（比如成本、剩余仓位、盈利数额等等）
        :param _stock_id:
        :param _obj_list:
        :return:
        """
        # 保存交易状态不为清仓的情况
        save_list = []
        for index, transaction_obj in enumerate(_obj_list):
            if transaction_obj['transaction_status'] == "未清仓":
                save_list.append(transaction_obj)

        # 专门处理不为清仓的状态
        for index, transaction_obj in enumerate(save_list):
            if index == 0:
                transaction_dict = {
                    # 剩余仓位等于第一次买入的数量
                    "remain_positions": int(transaction_obj['quantity']),
                    # 成本也等于第一次买入的价格
                    "cost": transaction_obj['buy_price'],
                    "business_id": transaction_obj['business_id']
                }
                order_crud.update_transaction_info(transaction_dict=transaction_dict)
                continue

            # 不为首个买入的状态
            if transaction_obj['transaction_type'] == '买入':
                # 此次买入的价格
                current_buy_price = transaction_obj['buy_price']
                # 此次买入的数量
                current_buy_quantity = int(transaction_obj['quantity'])
                # 获取上一条交易的成本价格
                # 上一条数据的业务id
                previous_obj_id = save_list[index - 1]['business_id']
                previous_obj = order_crud.get_transaction_info_by_id(data_id=previous_obj_id)
                previous_buy_price = previous_obj.cost
                # 上一条交易的剩余仓位
                previous_remain_quantity = int(previous_obj.remain_positions)

                # 计算此次的买入成本：(当前买入价格 x 当前买入的数量 + 上一条计算好的成本价格 * 上一条计算好的剩余仓位) / (当前买入的数量 + 上一条计算好的剩余数量)
                current_buy_cost = (
                                               current_buy_price * current_buy_quantity + previous_buy_price * previous_remain_quantity) / \
                                   (current_buy_quantity + previous_remain_quantity)
                # 计算此次的剩余数量（当前买入的数量 + 上一条计算好的剩余数量）
                current_remain_quantity = int(current_buy_quantity + previous_remain_quantity)

                # 更新数据库
                transaction_dict = {
                    # 剩余仓位等于第一次买入的数量
                    "remain_positions": current_remain_quantity,
                    # 成本也等于第一次买入的价格
                    "cost": current_buy_cost,
                    "business_id": transaction_obj['business_id']
                }
                order_crud.update_transaction_info(transaction_dict=transaction_dict)
            else:
                # 此次卖出的价格
                current_sell_price = transaction_obj['sell_price']
                # 此次卖出的股票数量
                current_sell_quantity = int(transaction_obj['quantity'])

                # 上一条交易的成本价格（此时成本还是为上一条的成本价，因为没有买入的操作，那么成本就不会更改）
                previous_obj_id = save_list[index - 1]['business_id']
                previous_obj = order_crud.get_transaction_info_by_id(data_id=previous_obj_id)
                previous_cost_price = previous_obj.cost
                # 上一条交易的剩余仓位
                previous_remain_quantity = int(previous_obj.remain_positions)

                # 计算此次的盈利：(此次卖出的价格 - 上一条交易的成本价) * 卖出数量
                current_profit_amount = (current_sell_price - previous_cost_price) * current_sell_quantity
                # 计算此次的剩余数量（上一条剩余仓位的数量 - 当前卖出的数量）
                current_remain_quantity = int(previous_remain_quantity - current_sell_quantity)

                # 更新数据库
                transaction_dict = {
                    "remain_positions": current_remain_quantity,
                    "cost": previous_cost_price,
                    # 盈利的数目
                    "profit_amount": current_profit_amount,
                    "business_id": transaction_obj['business_id']
                }
                order_crud.update_transaction_info(transaction_dict=transaction_dict)

                if int(current_remain_quantity) == 0:
                    # 直接清仓（要加个循环，直到当前索引进行清仓操作）
                    for _index in range(index + 1):
                        # 更新数据库
                        transaction_dict = {
                            "transaction_status": '已清仓',
                            "business_id": save_list[_index]['business_id']
                        }
                        order_crud.update_transaction_info(transaction_dict=transaction_dict)

                    # 清仓完之后需要再次进行迭代
                    _result = order_crud.get_stock_info_by_id(data_id=_stock_id)  # 未更新数据前的查询结果
                    _transaction_obj_list = _result.get("transaction_obj_list")
                    _transaction_obj_list = [_.as_dict() for _ in _transaction_obj_list]
                    _update_latest_transaction(_stock_id=_stock_id, _obj_list=_transaction_obj_list)

    _update_latest_transaction(_stock_id=stock_id, _obj_list=transaction_obj_list)

    # 获取股票信息
    result = order_crud.get_stock_info_by_id(data_id=stock_id)
    # 该股票的交易列表
    transaction_obj_list = result.get("transaction_obj_list")
    transaction_obj_list = [_.as_dict() for _ in transaction_obj_list]
    final_return_obj_list = time_to_timestamp(transaction_obj_list)

    return_data = {
        "Success": True,
        "code": 2000,
        "msg": "",
        "count": result.get('count'),
        "data": final_return_obj_list
    }

    return restful.ok(message="返回产品列表数据", data=return_data)


@stock_bp.route("/get_stock_list", methods=["GET"])
def get_stock_list():
    """
    获取所有的股票卡片列表
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

        # 总交易次数
        stock_list_obj['transaction_count'] = transaction_result_list.get("count")

        # 总盈利额
        total_profit_amount = 0.0
        for transaction_obj in transaction_obj_list:
            if transaction_obj.profit_amount:
                total_profit_amount += float(transaction_obj.profit_amount)
        stock_list_obj['total_profit_amount'] = "{:.2f}".format(total_profit_amount)

        # 获取最新的成本价 和 当前股票的状态（是否已清仓）
        # 查找所有的交易信息（只包含未清仓的信息）
        unclear_transaction_result_list = order_crud.get_unclear_transaction_by_stock_id(data_id=stock_business_id)
        if unclear_transaction_result_list:
            stock_list_obj['is_cleared'] = '未清仓'
            # 得到最新的成本价
            if unclear_transaction_result_list[-1].cost:
                stock_list_obj['latest_cost'] = "{:.2f}".format(unclear_transaction_result_list[-1].cost)
            else:
                stock_list_obj['latest_cost'] = 0.00
        else:
            stock_list_obj['is_cleared'] = '已清仓'
            stock_list_obj['latest_cost'] = 0.00

    data_list.sort(key=lambda x: x['is_cleared'] == '已清仓')  # 排个序
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


@stock_bp.route("/add_stock_list", methods=["POST"])
def add_stock_list():
    """
    添加股票列表
    :return:
    """
    auth_status = auth_check(user_token=request.headers.get('Authorization'), api='purchase_order/get_purchase_order')
    if AuthCheckEnum[auth_status].value is not True:
        return AuthCheckEnum[auth_status].value

    data = request.get_data(as_text=True)
    params_dict = json.loads(data)
    logger.info(
        "/add_stock_list 前端传入的参数为：\n{}".format(json.dumps(params_dict, indent=4, ensure_ascii=False))
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


@stock_bp.route("/update_stock_list", methods=["POST"])
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


@stock_bp.route("/del_stock", methods=["POST"])
def del_stock():
    """
    根据 stock ID 删除该股票和与之相关的股票交易信息
    :return:
    """
    auth_status = auth_check(user_token=request.headers.get('Authorization'), api='purchase_order/del_purchase_order')
    if AuthCheckEnum[auth_status].value is not True:
        return AuthCheckEnum[auth_status].value

    data = request.get_data(as_text=True)
    params_dict = json.loads(data)
    logger.info("/del_stock 前端传入的参数为：\n{}".format(json.dumps(params_dict, indent=4, ensure_ascii=False)))

    business_id = params_dict.get("stock_id")
    try:
        order_crud.del_stock_by_id(data_id=business_id)
    except:
        return restful.server_error(message=del_stock_failed)

    return restful.ok(message=del_stock_success)

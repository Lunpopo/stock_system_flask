from flask import Blueprint, request
from gkestor_common_logger import Logger

from app_router.models import stock_crud
from enums.enums import AuthCheckEnum
from utils import restful
from utils.authentication import auth_check

stock_statistics_bp = Blueprint("stock_statistics", __name__, url_prefix="/order_statistics")
logger = Logger()


# 获取股票统计信息：股票盈利总金额、总交易次数、总买入额、总卖出额
@stock_statistics_bp.route("/get_stock_statistics_info", methods=["GET"])
def get_stock_statistics_info():
    """
    获取股票统计信息：股票盈利总金额、总交易次数、总买入额、总卖出额
    :return:
    """
    auth_status = auth_check(user_token=request.headers.get('Authorization'),
                             api='order_statistics/get_purchase_price_statistics')
    if AuthCheckEnum[auth_status].value is not True:
        return AuthCheckEnum[auth_status].value

    result = stock_crud.get_stock_list()
    data_list = []
    for _ in result:
        _dict = _.as_dict()
        data_list.append(_dict)

    # 总交易次数
    total_transaction_count = 0
    # 总盈利额
    total_profit_amount = 0.0
    # 总买入额
    total_buy_amount = 0.0
    # 总卖出额
    total_sell_amount = 0.0

    # 增加一个产品采购单的种类
    for stock_list_obj in data_list:
        stock_business_id = stock_list_obj['business_id']
        transaction_result_list = stock_crud.get_transaction_by_stock_id(data_id=stock_business_id)
        transaction_obj_list = transaction_result_list.get("data")

        # 总交易次数
        total_transaction_count += int(transaction_result_list.get("count"))

        for transaction_obj in transaction_obj_list:
            if transaction_obj.profit_amount:
                total_profit_amount += float(transaction_obj.profit_amount)

            if transaction_obj.transaction_type == '买入':
                total_buy_amount += transaction_obj.subtotal_price
            elif transaction_obj.transaction_type == '卖出':
                total_sell_amount += transaction_obj.subtotal_price

    return_data = {
        "total_transaction_count": total_transaction_count,
        "total_profit_amount": total_profit_amount,
        "total_buy_amount": total_buy_amount,
        "total_sell_amount": total_sell_amount
    }
    return restful.ok(message="获取股票盈利总金额成功！！", data=return_data)


# 获取各个股票盈利饼图信息
@stock_statistics_bp.route("/get_profit_pie_statistics", methods=["GET"])
def get_profit_pie_statistics():
    """
    获取各个股票盈利饼图信息
    :return:
    """
    auth_status = auth_check(user_token=request.headers.get('Authorization'),
                             api='order_statistics/get_outbound_pie_statistics')
    if AuthCheckEnum[auth_status].value is not True:
        return AuthCheckEnum[auth_status].value

    result_data = stock_crud.get_profit_pie_statistic()

    dealer_names = []
    return_data = []
    for transaction_obj in result_data:
        stock_id = transaction_obj[0]
        stock_obj = stock_crud.get_stock_by_id(stock_id)
        name = stock_obj.stock_name
        _dict = {
            "name": name,
            "value": "{:.2f}".format(transaction_obj[1])
        }
        # 加入经销商的列表
        dealer_names.append(name)
        return_data.append(_dict)

    return restful.ok(
        message="获取各个股票盈利饼图信息成功！",
        data={"stock_names": dealer_names, "data_dict": return_data}
    )

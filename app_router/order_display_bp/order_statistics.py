import json

from flask import Blueprint, request
from gkestor_common_logger import Logger

from app_router.models import order_crud
from app_router.order_display_bp.order_lib import order_stock_data_list, search_stock_product
from enums.enums import AuthCheckEnum
from utils import restful
from utils.authentication import auth_check

order_statistics_bp = Blueprint("order_statistics", __name__, url_prefix="/order_statistics")
logger = Logger()


@order_statistics_bp.route("/get_transaction_list", methods=["GET"])
def get_transaction_list():
    """
    获取交易信息列表（前10的经销商数据）
    :return:
    """
    auth_status = auth_check(user_token=request.headers.get('Authorization'),
                             api='order_statistics/get_transaction_list')
    if AuthCheckEnum[auth_status].value is not True:
        return AuthCheckEnum[auth_status].value

    result_data = order_crud.get_outbound_transaction_statistic()
    dealer_names = []
    return_data = []
    index = 1
    for outbound_obj in result_data:
        _dict = {
            "index": index,
            # 经销商名称
            "name": outbound_obj[0],
            # 经销商的销售金额
            "outbound_price": outbound_obj[1]
        }
        # 加入经销商的列表
        dealer_names.append(outbound_obj[0])
        return_data.append(_dict)
        index += 1

    data = {
        'total': len(return_data),
        'items': return_data
    }
    return restful.ok(message="获取交易信息成功！", data=data)


@order_statistics_bp.route("/get_product_transaction_list", methods=["GET"])
def get_product_transaction_list():
    """
    获取产品交易信息列表（从销量最高的产品往下排列）
    :return:
    """
    auth_status = auth_check(user_token=request.headers.get('Authorization'),
                             api='order_statistics/get_product_transaction_list')
    if AuthCheckEnum[auth_status].value is not True:
        return AuthCheckEnum[auth_status].value

    result_data = order_crud.get_product_transaction_statistic()
    data = {
        'count': len(result_data),
        'items': result_data
    }
    return restful.ok(message="获取产品交易信息列表成功！", data=data)


@order_statistics_bp.route("/get_stock_all_data", methods=["GET"])
def get_stock_all_data():
    """
    获取总库存数据信息-用于下载
    :return:
    """
    auth_status = auth_check(user_token=request.headers.get('Authorization'), api='order_statistics/get_stock_all_data')
    if AuthCheckEnum[auth_status].value is not True:
        return AuthCheckEnum[auth_status].value

    # 名称搜索
    product_name = request.args.get("title")

    params_dict = {"product_name": product_name}
    logger.info("/get_stock_all_data 前端的入参参数：\n{}".format(json.dumps(params_dict, indent=4, ensure_ascii=False)))

    # 获取所有的库存数据
    stock_obj_list = order_crud.cal_stock_list()
    # 搜索
    data_list = search_stock_product(stock_obj_list, product_name)
    # 按数量排序
    data_list = order_stock_data_list(data_list)

    return_data = {
        "Success": True,
        "code": 2000,
        "msg": "",
        "count": len(data_list),
        "data": data_list
    }
    return restful.ok(message="返回产品列表数据", data=return_data)


@order_statistics_bp.route("/get_outbound_stock_data_list", methods=["GET"])
def get_outbound_stock_data_list():
    """
    获取出库数据信息
    :return:
    """
    auth_status = auth_check(user_token=request.headers.get('Authorization'),
                             api='order_statistics/get_outbound_stock_data_list')
    if AuthCheckEnum[auth_status].value is not True:
        return AuthCheckEnum[auth_status].value

    page = int(request.args.get("page"))
    limit = int(request.args.get("limit"))
    # 名称搜索
    product_name = request.args.get("title")

    params_dict = {"page": page, "limit": limit, 'product_name': product_name}
    logger.info("/get_outbound_stock_data_list 前端的入参参数：\n{}".format(
        json.dumps(params_dict, indent=4, ensure_ascii=False))
    )

    # 获取出库库存数据
    outbound_stock_obj_list = order_crud.cal_outbound_stock_list()
    outbound_stock_obj_list = [_.get("product_obj") for _ in outbound_stock_obj_list]

    # 搜索
    data_list = search_stock_product(outbound_stock_obj_list, product_name)
    # 按数量排序
    data_list = order_stock_data_list(data_list)

    # 利用page、limit、order_by 做分页和排序
    # 前端page从1开始
    page -= 1
    page = page * limit
    paginate_list = data_list[page: page + limit]
    return_data = {
        "Success": True,
        "code": 2000,
        "msg": "",
        "count": len(data_list),
        "data": paginate_list
    }
    return restful.ok(message="返回产品列表数据", data=return_data)


@order_statistics_bp.route("/get_stock_data_list", methods=["GET"])
def get_stock_data_list():
    """
    获取总库存数据信息（表格展示信息）
    :return:
    """
    auth_status = auth_check(user_token=request.headers.get('Authorization'),
                             api='order_statistics/get_stock_data_list')
    if AuthCheckEnum[auth_status].value is not True:
        return AuthCheckEnum[auth_status].value

    page = int(request.args.get("page"))
    limit = int(request.args.get("limit"))
    # 名称搜索
    product_name = request.args.get("title")

    params_dict = {"page": page, "limit": limit, "product_name": product_name}
    logger.info("/get_stock_data_list 前端的入参参数：\n{}".format(json.dumps(params_dict, indent=4, ensure_ascii=False)))

    # 获取所有的库存数据
    stock_obj_list = order_crud.cal_stock_list()

    # 搜索
    data_list = search_stock_product(stock_obj_list, product_name)
    # 按数量排序
    data_list = order_stock_data_list(data_list)

    # 利用page、limit、order_by 做分页和排序
    # 前端page从1开始
    page -= 1
    page = page * limit
    paginate_list = data_list[page: page + limit]
    return_data = {
        "Success": True,
        "code": 2000,
        "msg": "",
        "count": len(data_list),
        "data": paginate_list
    }
    return restful.ok(message="返回产品列表数据", data=return_data)


@order_statistics_bp.route("/get_outbound_pie_statistics", methods=["GET"])
def get_outbound_pie_statistics():
    """
    获取各个经销商的出库单的金额统计饼图信息
    :return:
    """
    auth_status = auth_check(user_token=request.headers.get('Authorization'),
                             api='order_statistics/get_outbound_pie_statistics')
    if AuthCheckEnum[auth_status].value is not True:
        return AuthCheckEnum[auth_status].value

    result_data = order_crud.get_outbound_pie_statistic()

    dealer_names = []
    return_data = []
    for outbound_obj in result_data:
        _dict = {
            # 经销商名称
            "name": outbound_obj[0],
            # 经销商的销售金额
            "value": outbound_obj[1]
        }
        # 加入经销商的列表
        dealer_names.append(outbound_obj[0])
        return_data.append(_dict)

    return restful.ok(
        message="获取各个经销商出库金额统计信息成功！",
        data={"dealer_names": dealer_names, "data_dict": return_data}
    )


@order_statistics_bp.route("/get_outbound_bar_statistics", methods=["GET"])
def get_outbound_bar_statistics():
    """
    获取各个经销商的出库单的金额统计 柱状图 信息
    :return:
    """
    auth_status = auth_check(user_token=request.headers.get('Authorization'),
                             api='order_statistics/get_outbound_bar_statistics')
    if AuthCheckEnum[auth_status].value is not True:
        return AuthCheckEnum[auth_status].value
    result_data = order_crud.get_outbound_bar_statistic()
    return restful.ok(message="获取各个经销商出库金额统计信息成功！", data=result_data)


@order_statistics_bp.route("/get_outbound_price_statistics", methods=["GET"])
def get_outbound_price_statistics():
    """
    获取出库单的金额统计信息
    :return:
    """
    auth_status = auth_check(user_token=request.headers.get('Authorization'),
                             api='order_statistics/get_outbound_price_statistics')
    if AuthCheckEnum[auth_status].value is not True:
        return AuthCheckEnum[auth_status].value

    result_data = order_crud.get_outbound_statistic()
    data_list = []
    for _ in result_data:
        _dict = _.as_dict()
        data_list.append(_dict)

    # 统计图的横坐标
    x = []
    # 统计图的纵坐标
    y = []
    for outbound_obj in data_list:
        x.append(outbound_obj.get('create_time'))
        y.append(outbound_obj.get("total_price"))

    data = {
        "x": x,
        "y": y
    }
    return restful.ok(message="获取出库单金额统计信息成功！", data=data)


@order_statistics_bp.route("/get_outbound_piece_statistics", methods=["GET"])
def get_outbound_piece_statistics():
    """
    获取出库单的数量统计信息
    :return:
    """
    auth_status = auth_check(user_token=request.headers.get('Authorization'),
                             api='order_statistics/get_outbound_piece_statistics')
    if AuthCheckEnum[auth_status].value is not True:
        return AuthCheckEnum[auth_status].value

    result_data = order_crud.get_outbound_statistic()
    data_list = []
    for _ in result_data:
        _dict = _.as_dict()
        data_list.append(_dict)

    # 统计图的横坐标
    x = []
    # 统计图的纵坐标
    y = []
    for outbound_obj in data_list:
        # 用创建时间（这样更改了订单内容也不会改变该条数据的排序）
        x.append(outbound_obj.get('create_time'))
        y.append(outbound_obj.get("total_piece"))

    data = {
        "x": x,
        "y": y
    }
    return restful.ok(message="获取出库单数量统计信息成功！", data=data)


@order_statistics_bp.route("/get_total_outbound_price_and_piece", methods=["GET"])
def get_total_outbound_price_and_piece():
    """
    获取出库单的总金额和总数量
    :return:
    """
    auth_status = auth_check(user_token=request.headers.get('Authorization'),
                             api='order_statistics/get_total_outbound_price_and_piece')
    if AuthCheckEnum[auth_status].value is not True:
        return AuthCheckEnum[auth_status].value

    order_total_price = order_crud.get_total_outbound_price()
    order_total_piece = order_crud.get_total_outbound_piece()
    data = {
        "total_price": order_total_price,
        "total_piece": int(order_total_piece)
    }
    return restful.ok(message="获取出库单总金额成功！", data=data)


@order_statistics_bp.route("/get_outbound_stock_all_data", methods=["GET"])
def get_outbound_stock_all_data():
    """
    获取出库数据信息-用于下载
    :return:
    """
    auth_status = auth_check(user_token=request.headers.get('Authorization'),
                             api='order_statistics/get_outbound_stock_all_data')
    if AuthCheckEnum[auth_status].value is not True:
        return AuthCheckEnum[auth_status].value

    # 名称搜索
    product_name = request.args.get("title")

    params_dict = {'product_name': product_name}
    logger.info("/get_outbound_stock_all_data 前端的入参参数：\n{}".format(
        json.dumps(params_dict, indent=4, ensure_ascii=False))
    )

    # 获取出库库存数据
    outbound_stock_obj_list = order_crud.cal_outbound_stock_list()
    outbound_stock_obj_list = [_.get("product_obj") for _ in outbound_stock_obj_list]
    # 搜索
    data_list = search_stock_product(outbound_stock_obj_list, product_name)
    # 按数量排序
    data_list = order_stock_data_list(data_list)

    return_data = {
        "Success": True,
        "code": 2000,
        "msg": "",
        "count": len(data_list),
        "data": data_list
    }
    return restful.ok(message="返回产品列表数据", data=return_data)


@order_statistics_bp.route("/get_purchase_stock_all_data", methods=["GET"])
def get_purchase_stock_all_data():
    """
    获取入库数据信息-用于下载
    :return:
    """
    auth_status = auth_check(user_token=request.headers.get('Authorization'),
                             api='order_statistics/get_purchase_stock_all_data')
    if AuthCheckEnum[auth_status].value is not True:
        return AuthCheckEnum[auth_status].value

    # 名称搜索
    product_name = request.args.get("title")

    params_dict = {"product_name": product_name}
    logger.info("/get_purchase_stock_all_data 前端的入参参数：\n{}".format(
        json.dumps(params_dict, indent=4, ensure_ascii=False))
    )

    # 获取入库库存数据
    purchase_stock_obj_list = order_crud.cal_purchase_stock_list()
    purchase_stock_obj_list = [_.get("product_obj") for _ in purchase_stock_obj_list]
    # 搜索
    data_list = search_stock_product(purchase_stock_obj_list, product_name)
    # 按数量排序
    data_list = order_stock_data_list(data_list)

    return_data = {
        "Success": True,
        "code": 2000,
        "msg": "",
        "count": len(data_list),
        "data": data_list
    }
    return restful.ok(message="返回产品列表数据", data=return_data)


@order_statistics_bp.route("/get_purchase_stock_data_list", methods=["GET"])
def get_purchase_stock_data_list():
    """
    获取入库数据信息
    :return:
    """
    auth_status = auth_check(user_token=request.headers.get('Authorization'),
                             api='order_statistics/get_purchase_stock_data_list')
    if AuthCheckEnum[auth_status].value is not True:
        return AuthCheckEnum[auth_status].value

    page = int(request.args.get("page"))
    limit = int(request.args.get("limit"))
    # 名称搜索
    product_name = request.args.get("title")

    params_dict = {"page": page, "limit": limit, 'product_name': product_name}
    logger.info("/get_purchase_stock_data_list 前端的入参参数：\n{}".format(
        json.dumps(params_dict, indent=4, ensure_ascii=False))
    )

    # 获取入库库存数据
    purchase_stock_obj_list = order_crud.cal_purchase_stock_list()
    purchase_stock_obj_list = [_.get("product_obj") for _ in purchase_stock_obj_list]
    # 搜索
    data_list = search_stock_product(purchase_stock_obj_list, product_name)
    # 按数量排序
    data_list = order_stock_data_list(data_list)

    # 利用page、limit、order_by 做分页和排序
    # 前端page从1开始
    page -= 1
    page = page * limit
    paginate_list = data_list[page: page + limit]
    return_data = {
        "Success": True,
        "code": 2000,
        "msg": "",
        "count": len(data_list),
        "data": paginate_list
    }
    return restful.ok(message="返回产品列表数据", data=return_data)


@order_statistics_bp.route("/get_purchase_price_statistics", methods=["GET"])
def get_purchase_price_statistics():
    """
    获取入库单的金额统计信息
    :return:
    """
    auth_status = auth_check(user_token=request.headers.get('Authorization'),
                             api='order_statistics/get_purchase_price_statistics')
    if AuthCheckEnum[auth_status].value is not True:
        return AuthCheckEnum[auth_status].value

    result_data = order_crud.get_purchase_statistic()
    data_list = []
    for _ in result_data:
        _dict = _.as_dict()
        data_list.append(_dict)

    # 统计图的横坐标
    x = []
    # 统计图的纵坐标
    y = []
    for purchase_obj in data_list:
        x.append(purchase_obj.get('create_time'))
        y.append(purchase_obj.get("total_price"))

    data = {
        "x": x,
        "y": y
    }
    return restful.ok(message="获取入库单金额统计信息成功！", data=data)


@order_statistics_bp.route("/get_purchase_piece_statistics", methods=["GET"])
def get_purchase_piece_statistics():
    """
    获取入库单的数量统计信息
    :return:
    """
    auth_status = auth_check(user_token=request.headers.get('Authorization'),
                             api='order_statistics/get_purchase_piece_statistics')
    if AuthCheckEnum[auth_status].value is not True:
        return AuthCheckEnum[auth_status].value

    result_data = order_crud.get_purchase_statistic()
    data_list = []
    for _ in result_data:
        _dict = _.as_dict()
        data_list.append(_dict)

    # 统计图的横坐标
    x = []
    # 统计图的纵坐标
    y = []
    for purchase_obj in data_list:
        x.append(purchase_obj.get('create_time'))
        y.append(purchase_obj.get("total_piece"))

    data = {
        "x": x,
        "y": y
    }
    return restful.ok(message="获取入库单数量统计信息成功！", data=data)


@order_statistics_bp.route("/get_total_purchase_price_and_piece", methods=["GET"])
def get_total_purchase_price_and_piece():
    """
    获取入库单的总金额和总数量
    :return:
    """
    auth_status = auth_check(
        user_token=request.headers.get('Authorization'), api='order_statistics/get_total_purchase_price_and_piece'
    )
    if AuthCheckEnum[auth_status].value is not True:
        return AuthCheckEnum[auth_status].value

    order_total_price = order_crud.get_total_purchase_price()
    order_total_piece = order_crud.get_total_purchase_piece()
    data = {
        "total_price": order_total_price,
        "total_piece": order_total_piece
    }
    return restful.ok(message="获取入库单总金额成功！", data=data)

import json
import time

from flask import Blueprint, request
from gkestor_common_logger import Logger

from app_router.models import order_crud, crud
from enums.enums import AuthCheckEnum
from messages.messages import *
from utils import restful
from utils.authentication import auth_check
from utils.date_utils import time_to_timestamp

purchase_order_bp = Blueprint("purchase_order", __name__, url_prefix="/purchase_order")
logger = Logger()


@purchase_order_bp.route("/get_purchase_order", methods=["GET"])
def get_purchase_order():
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
    logger.info("/get_purchase_order 前端的入参参数：\n{}".format(json.dumps(params_dict, indent=4, ensure_ascii=False)))

    # 前端page从1开始
    page -= 1
    page = page * limit
    result = order_crud.get_purchase_order_limit(page=page, limit=limit)
    result_data = result.get("data")
    data_list = []
    for _ in result_data:
        _dict = _.as_dict()
        data_list.append(_dict)

    # 增加一个产品采购单的种类
    for purchase_result_obj in data_list:
        purchase_business_id = purchase_result_obj['business_id']
        purchase_list_result = order_crud.get_products_by_purchase_order_id(data_id=purchase_business_id)
        purchase_result_obj['type'] = purchase_list_result.get("count")

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


@purchase_order_bp.route("/get_purchase_product_details", methods=["GET"])
def get_purchase_product_details():
    """
    获取入库单的产品列表详情信息
    :return:
    """
    auth_status = auth_check(user_token=request.headers.get('Authorization'),
                             api='purchase_order/get_purchase_product_details')
    if AuthCheckEnum[auth_status].value is not True:
        return AuthCheckEnum[auth_status].value

    # 入库订单ID
    purchase_order_id = request.args.get("purchase_order_id")

    params_dict = {"purchase_order_id": purchase_order_id}
    logger.info("/get_purchase_product_details 前端的入参参数：\n{}".format(
        json.dumps(params_dict, indent=4, ensure_ascii=False))
    )

    data_list = []
    result = order_crud.get_products_by_purchase_order_id(data_id=purchase_order_id)
    # 该入库订单下的所有产品
    result_data = result.get("data")
    for data_obj in result_data:
        purchase_product_id = data_obj.get('product_id')
        product_obj = crud.get_product_by_business_id(business_id=purchase_product_id)

        _dict = {
            'product_id': purchase_product_id,
            'product_name': product_obj.product_name,
            'scent_type': product_obj.scent_type,
            "specifications": product_obj.specifications,
            "specification_of_piece": product_obj.specification_of_piece,
            "unit_price": product_obj.unit_price,
            "img_url": product_obj.img_url,
            "thumb_img_url": product_obj.thumb_img_url,
            "quantity": data_obj.get('quantity'),
            "subtotal_price": data_obj.get('subtotal_price'),
            "remarks": data_obj.get('remarks')
        }
        data_list.append(_dict)

    return_data = {
        "Success": True,
        "code": 2000,
        "msg": "",
        "count": result.get('count'),
        "data": data_list
    }
    return restful.ok(message="返回产品列表数据", data=return_data)


@purchase_order_bp.route("/add_purchase_order", methods=["POST"])
def add_purchase_order():
    """
    新增一条入库单
    :return:
    """
    auth_status = auth_check(user_token=request.headers.get('Authorization'), api='purchase_order/add_purchase_order')
    if AuthCheckEnum[auth_status].value is not True:
        return AuthCheckEnum[auth_status].value

    data = request.get_data(as_text=True)
    params_dict = json.loads(data)
    logger.info(
        "/add_purchase_order 前端传入的参数为：\n{}".format(json.dumps(params_dict, indent=4, ensure_ascii=False))
    )

    title = params_dict.get("title")
    domains = params_dict.get("domains")
    total_price = params_dict.get("total_price")
    total_piece = params_dict.get("total_piece")
    remarks = params_dict.get("remarks")

    if domains:
        purchase_order_dict = {
            "title": title,
            "total_price": total_price,
            "total_piece": total_piece,
            "remarks": remarks
        }
        # 新增一条入库单数据，并返回入库单的 业务id
        purchase_order_obj = order_crud.add_purchase_order(data=purchase_order_dict)

        if purchase_order_obj:
            for single_product_obj in domains:
                # 单条产品列表
                single_product_dict = {
                    "purchase_order_id": purchase_order_obj.business_id,
                    "product_id": single_product_obj.get('business_id'),
                    "quantity": single_product_obj.get("quantity"),
                    "subtotal_price": single_product_obj.get("subtotal_price"),
                    "remarks": single_product_obj.get("remarks")
                }
                # 添加本条产品记录到 purchase_order_list 表里面
                order_crud.add_purchase_product(data=single_product_dict)

        else:
            return restful.server_error(message=add_purchase_order_failed)

        return restful.ok(message=add_purchase_order_success)
    return restful.server_error(message=add_purchase_order_not_zero)


@purchase_order_bp.route("/update_purchase_order", methods=["POST"])
def update_purchase_order():
    """
    更新入库单信息
    :return:
    """
    auth_status = auth_check(user_token=request.headers.get('Authorization'),
                             api='purchase_order/update_purchase_order')
    if AuthCheckEnum[auth_status].value is not True:
        return AuthCheckEnum[auth_status].value

    data = request.get_data(as_text=True)
    params_dict = json.loads(data)
    logger.info(
        "/update_purchase_order 前端传入的参数为：\n{}".format(json.dumps(params_dict, indent=4, ensure_ascii=False))
    )

    title = params_dict.get("title")
    domains = params_dict.get("domains")
    total_price = params_dict.get("total_price")
    total_piece = params_dict.get("total_piece")
    remarks = params_dict.get("remarks")
    order_business_id = params_dict.get("business_id")
    create_time = params_dict.get("create_time")

    if domains:
        if create_time is not None:
            create_time = int(create_time / 1000)
            create_time_array = time.localtime(create_time)
            create_time = time.strftime("%Y-%m-%d %H:%M:%S", create_time_array)
            purchase_order_dict = {
                "title": title,
                "total_price": total_price,
                "total_piece": total_piece,
                "remarks": remarks,
                "create_time": create_time
            }
        else:
            purchase_order_dict = {
                "title": title,
                "total_price": total_price,
                "total_piece": total_piece,
                "remarks": remarks
            }
        # 1. 先更新入库单数据
        order_crud.update_purchase_by_business_id(
            data_id=order_business_id, data=purchase_order_dict
        )

        # 2. 更新关联产品表之前先删除相关的产品，后面再添加
        order_crud.del_purchase_product_by_id(data_id=order_business_id)
        # 3. 添加产品列表 到 订单产品关联表
        for single_product_obj in domains:
            if single_product_obj.get("product_id") is not None:
                product_id = single_product_obj.get("product_id")
            else:
                product_id = single_product_obj.get("business_id")

            # 单条产品列表
            single_product_dict = {
                "purchase_order_id": order_business_id,
                "product_id": product_id,
                "quantity": single_product_obj.get("quantity"),
                "subtotal_price": single_product_obj.get("subtotal_price"),
                "remarks": single_product_obj.get("remarks")
            }
            # 添加本条产品记录到 purchase_order_list 表里面
            order_crud.add_purchase_product(data=single_product_dict)

        return restful.ok(message=add_purchase_order_success)
    return restful.server_error(message=add_purchase_order_not_zero)


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

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

outbound_order_bp = Blueprint("outbound_order", __name__, url_prefix="/outbound_order")
logger = Logger()


@outbound_order_bp.route("/get_outbound_order", methods=["GET"])
def get_outbound_order():
    """
    获取出库单列表
    :return:
    """
    auth_status = auth_check(user_token=request.headers.get('Authorization'), api='outbound_order/get_outbound_order')
    if AuthCheckEnum[auth_status].value is not True:
        return AuthCheckEnum[auth_status].value

    page = int(request.args.get("page"))
    limit = int(request.args.get("limit"))
    dealer_name = request.args.get('dealer_name')

    params_dict = {"page": page, "limit": limit, 'dealer_name': dealer_name}
    logger.info("/get_outbound_order 前端的入参参数：\n{}".format(json.dumps(params_dict, indent=4, ensure_ascii=False)))

    # 前端page从1开始
    page -= 1
    page = page * limit
    result = order_crud.get_outbound_order_limit(page=page, limit=limit, dealer_name=dealer_name)
    result_data = result.get("data")
    data_list = []
    for _ in result_data:
        _dict = _.as_dict()
        data_list.append(_dict)

    # 增加一个产品出库的种类
    for outbound_result_obj in data_list:
        outbound_business_id = outbound_result_obj['business_id']
        outbound_list_result = order_crud.get_products_by_outbound_order_id(data_id=outbound_business_id)
        outbound_result_obj['type'] = outbound_list_result.get("count")

    # 统一转换成时间戳的形式
    data_list = time_to_timestamp(data_list)

    return_data = {
        "Success": True,
        "code": 2000,
        "msg": "",
        "count": result.get('count'),
        "data": data_list
    }

    return restful.ok(message="返回出库单列表数据", data=return_data)


@outbound_order_bp.route("/get_outbound_product_details", methods=["GET"])
def get_outbound_product_details():
    """
    获取出库单的产品列表详情信息
    :return:
    """
    auth_status = auth_check(user_token=request.headers.get('Authorization'),
                             api='outbound_order/get_outbound_product_details')
    if AuthCheckEnum[auth_status].value is not True:
        return AuthCheckEnum[auth_status].value

    # 出库单ID
    outbound_order_id = request.args.get("outbound_order_id")

    params_dict = {"outbound_order_id": outbound_order_id}
    logger.info("/get_outbound_product_details 前端的入参参数：\n{}".format(
        json.dumps(params_dict, indent=4, ensure_ascii=False))
    )

    # 根据 订单id 获取所有的产品列表信息
    result = order_crud.get_products_by_outbound_order_id(data_id=outbound_order_id)
    data_list = result.get("data")  # 所有的产品
    for data_obj in data_list:
        dealer_product_id = data_obj.get('dealer_product_id')
        dealer_product_obj = order_crud.get_products_by_dealer_product_id(dealer_product_id=dealer_product_id)
        _dict = dealer_product_obj.as_dict()
        product_obj = crud.get_product_by_business_id(business_id=dealer_product_obj.product_id)

        data_obj['product_name'] = product_obj.product_name
        data_obj['specifications'] = product_obj.specifications
        data_obj['scent_type'] = product_obj.scent_type
        data_obj['specification_of_piece'] = product_obj.specification_of_piece
        data_obj['thumb_img_url'] = product_obj.thumb_img_url
        data_obj['img_url'] = product_obj.img_url

        data_obj['belong_to'] = _dict.get('belong_to')
        data_obj['unit_price'] = _dict.get('unit_price')

    return_data = {
        "Success": True,
        "code": 2000,
        "msg": "",
        "count": result.get('count'),
        "data": data_list
    }
    return restful.ok(message="返回出库单列表数据", data=return_data)


@outbound_order_bp.route("/add_outbound_order", methods=["POST"])
def add_outbound_order():
    """
    新增一条出库单
    :return:
    """
    auth_status = auth_check(user_token=request.headers.get('Authorization'), api='outbound_order/add_outbound_order')
    if AuthCheckEnum[auth_status].value is not True:
        return AuthCheckEnum[auth_status].value

    data = request.get_data(as_text=True)
    params_dict = json.loads(data)
    logger.info("/add_outbound_order 前端传入的参数为：\n{}".format(json.dumps(params_dict, indent=4, ensure_ascii=False)))

    title = params_dict.get("title")
    belong_to = params_dict.get("belong_to")
    domains = params_dict.get("domains")
    total_price = params_dict.get("total_price")
    total_piece = params_dict.get("total_piece")
    remarks = params_dict.get("remarks")
    phone = params_dict.get("phone")
    address = params_dict.get("address")
    logistics_company = params_dict.get("logistics_company")
    logistics_num = params_dict.get("logistics_num")

    if domains:
        outbound_order_dict = {
            "title": title,
            "belong_to": belong_to,
            "total_price": total_price,
            "total_piece": total_piece,
            "phone": phone,
            "address": address,
            "logistics_company": logistics_company,
            "logistics_num": logistics_num,
            "remarks": remarks
        }
        # 新增一条出库单数据，并返回出库单的 业务id
        outbound_order_obj = order_crud.add_outbound_order(data=outbound_order_dict)

        if domains and outbound_order_obj:
            for single_product_obj in domains:
                # 单条产品列表
                single_product_dict = {
                    "outbound_order_id": outbound_order_obj.business_id,
                    "dealer_product_id": single_product_obj.get("business_id"),
                    "quantity": single_product_obj.get("quantity"),
                    "subtotal_price": single_product_obj.get("subtotal_price"),
                    # 这个remark 不是 product表的remark，而是添加出库订单产品的remark，单独的
                    "remarks": single_product_obj.get("product_remarks")
                }
                # 添加本条产品记录到 outbound_order_list 表里面
                order_crud.add_outbound_product(data=single_product_dict)

        else:
            return restful.server_error(message=add_outbound_order_failed)

        return restful.ok(message=add_outbound_order_success)
    else:
        return restful.server_error(message=add_outbound_order_not_zero)


@outbound_order_bp.route("/update_outbound_order", methods=["POST"])
def update_outbound_order():
    """
    更新出库单
    :return:
    """
    auth_status = auth_check(user_token=request.headers.get('Authorization'),
                             api='outbound_order/update_outbound_order')
    if AuthCheckEnum[auth_status].value is not True:
        return AuthCheckEnum[auth_status].value

    data = request.get_data(as_text=True)
    params_dict = json.loads(data)
    logger.info("/update_outbound_order 前端传入的参数为：\n{}".format(
        json.dumps(params_dict, indent=4, ensure_ascii=False))
    )

    title = params_dict.get("title")
    belong_to = params_dict.get("belong_to")
    domains = params_dict.get("domains")
    total_price = params_dict.get("total_price")
    total_piece = params_dict.get("total_piece")
    remarks = params_dict.get("remarks")
    phone = params_dict.get("phone")
    address = params_dict.get("address")
    logistics_company = params_dict.get("logistics_company")
    logistics_num = params_dict.get("logistics_num")
    order_business_id = params_dict.get("business_id")
    create_time = params_dict.get('create_time')

    if domains:
        if create_time is not None:
            create_time = int(create_time / 1000)
            create_time_array = time.localtime(create_time)
            create_time = time.strftime("%Y-%m-%d %H:%M:%S", create_time_array)

            outbound_order_dict = {
                "title": title,
                "belong_to": belong_to,
                "total_price": total_price,
                "total_piece": total_piece,
                "phone": phone,
                "address": address,
                "logistics_company": logistics_company,
                "logistics_num": logistics_num,
                "remarks": remarks,
                "create_time": create_time
            }
        else:
            outbound_order_dict = {
                "title": title,
                "belong_to": belong_to,
                "total_price": total_price,
                "total_piece": total_piece,
                "phone": phone,
                "address": address,
                "logistics_company": logistics_company,
                "logistics_num": logistics_num,
                "remarks": remarks
            }
        # 更新出库单数据
        order_crud.update_outbound_by_business_id(
            data_id=order_business_id, data=outbound_order_dict
        )

        # 更新关联产品表之前先删除相关的产品，后面再添加
        order_crud.del_outbound_order_product(data_id=order_business_id)
        # 添加产品列表 到 订单产品关联表
        for single_product_obj in domains:
            if single_product_obj.get("dealer_product_id") is not None:
                dealer_product_id = single_product_obj.get("dealer_product_id")
            else:
                dealer_product_id = single_product_obj.get("business_id")
            # 单条产品列表
            single_product_dict = {
                "outbound_order_id": order_business_id,
                "dealer_product_id": dealer_product_id,
                "quantity": single_product_obj.get("quantity"),
                "subtotal_price": single_product_obj.get("subtotal_price"),
                # 这个remark 不是 product表的remark，而是添加出库订单产品的remark，单独的
                "remarks": single_product_obj.get("product_remarks")
            }
            # 添加本条产品记录到 outbound_order_list 表里面
            order_crud.add_outbound_product(data=single_product_dict)

        return restful.ok(message=update_outbound_order_success)
    else:
        return restful.server_error(message=update_outbound_order_not_zero)


@outbound_order_bp.route("/del_outbound_order", methods=["POST"])
def del_outbound_order():
    """
    根据 订单ID 删除一条出库单
    :return:
    """
    auth_status = auth_check(user_token=request.headers.get('Authorization'), api='outbound_order/del_outbound_order')
    if AuthCheckEnum[auth_status].value is not True:
        return AuthCheckEnum[auth_status].value

    data = request.get_data(as_text=True)
    params_dict = json.loads(data)
    logger.info("/del_outbound_order 前端传入的参数为：\n{}".format(json.dumps(params_dict, indent=4, ensure_ascii=False)))

    business_id = params_dict.get("outbound_order_id")
    try:
        order_crud.del_outbound_order_by_id(data_id=business_id)
    except:
        return restful.server_error(message=del_outbound_order_failed)

    return restful.ok(message=del_outbound_order_success)

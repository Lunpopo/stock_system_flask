from sqlalchemy import func, desc
from sqlalchemy.orm import aliased

from app_router.models.database import db
from app_router.models.models import PurchaseOrder, PurchaseOrderList, OutboundOrder, OutboundOrderList, \
    DealerProductList, ProductList
from app_router.order_display_bp.order_lib import format_purchase_product, format_outbound_product
from exceptions.order_exception import *


def duplicate_remove_outbound_product(outbound_product_list):
    """
    对出库单的数据进行去重
    :param outbound_product_list:
    :return: 出库单的去重对象列表，出库单的去重对象列表，例如：
    [{
        'product_tuple': ('乾隆卅一（瓶装）53度（活动搭赠）', '清香型', 1000)
        'product_obj': {'id': 'b89c4166-d11f-4dc4-b39f-3facad00555c', 'product_name': '乾隆卅一（瓶装）53度（活动搭赠）'}
    }]
    """
    duplicate_remove_outbound = []
    # 处理出库单
    for product_obj in outbound_product_list:
        product_name = product_obj.get("product_name")
        if "活动" in product_name:
            product_name = product_name.split("（活动）")[0]
            product_obj['product_name'] = product_name

        # 三个指标唯一确定一个产品：产品名、香型、规格
        _dict = {
            "product_tuple": (
                product_name, product_obj.get('scent_type'), product_obj.get('specifications')
            ),
            "product_obj": product_obj,
        }
        is_exist = False
        for _index, _ in enumerate(duplicate_remove_outbound):
            if _dict.get("product_tuple") == _.get('product_tuple'):
                is_exist = True
                # 叠加（出库单的数量就是（瓶），所以不需要乘以规格）
                current_quantity = product_obj.get('quantity') + _.get("product_obj").get('quantity')
                _dict['product_obj']['quantity'] = current_quantity
                duplicate_remove_outbound[_index] = _dict
                break
        if not is_exist:
            duplicate_remove_outbound.append(_dict)

    return duplicate_remove_outbound


def duplicate_remove_purchase_product(purchase_product_list):
    """
    对入库单的数据进行去重
    :param purchase_product_list:
    :return: 入库单的去重对象列表，例如：
    [{
        'product_tuple': ('乾隆卅一（瓶装）53度（活动搭赠）', '清香型', 1000)
        'product_obj': {'id': 'b89c4166-d11f-4dc4-b39f-3facad00555c', 'product_name': '乾隆卅一（瓶装）53度（活动搭赠）'}
    }]
    """
    # 去重合并
    duplicate_remove_purchase = []

    # 处理入库单
    for product_obj in purchase_product_list:
        product_name = product_obj.get("product_name")
        # 三个指标唯一确定一个产品：产品名、香型、规格
        if "活动" in product_name:
            product_name = product_name.split("（活动）")[0]
            product_obj['product_name'] = product_name

        _dict = {
            "product_tuple": (
                product_name, product_obj.get('scent_type'), product_obj.get('specifications')
            ),
            "product_obj": product_obj,
        }
        is_exist = False
        for _index, _ in enumerate(duplicate_remove_purchase):
            if _dict.get("product_tuple") == _.get('product_tuple'):
                is_exist = True
                # 叠加，瓶数 = product_obj.get('quantity') * product_obj.get("specification_of_piece")，
                # _.get("product_obj").get("quantity) 单位已经是瓶数了
                current_quantity = product_obj.get('quantity') * product_obj.get("specification_of_piece") + _.get(
                    "product_obj").get('quantity')
                _dict['product_obj']['quantity'] = current_quantity
                duplicate_remove_purchase[_index] = _dict
                break
        if not is_exist:
            # 叠加
            current_quantity = _dict['product_obj'].get('quantity') * _dict['product_obj'].get("specification_of_piece")
            _dict['product_obj']['quantity'] = current_quantity
            duplicate_remove_purchase.append(_dict)

    return duplicate_remove_purchase


def cal_stock(purchase_list, outbound_list):
    """
    计算剩余库存
    :param purchase_list: 入库产品的所有数量数据
    :param outbound_list: 出库产品的所有数量数据
    :return:
    """
    # 计算剩余库存数量
    return_stock_list = []
    for purchase_dict in purchase_list:
        is_exist = False
        for outbound_dict in outbound_list:
            if purchase_dict.get("product_tuple") == outbound_dict.get("product_tuple"):
                is_exist = True

                # 入库的数量
                purchase_dict['product_obj']['purchase_quantity'] = purchase_dict.get('product_obj').get('quantity')

                # 计算剩余库存的容量
                purchase_dict['product_obj']['quantity'] = purchase_dict.get('product_obj').get(
                    'quantity') - outbound_dict.get('product_obj').get('quantity')

                # 计算出库的数量
                if purchase_dict['product_obj'].get('outbound_quantity'):
                    purchase_dict['product_obj']['outbound_quantity'] = purchase_dict['product_obj'].get(
                        'outbound_quantity') + outbound_dict.get('product_obj').get('quantity')
                else:
                    purchase_dict['product_obj']['outbound_quantity'] = outbound_dict.get('product_obj').get('quantity')

                # 保存
                return_stock_list.append(purchase_dict['product_obj'])
                break

        if not is_exist:
            purchase_dict["product_obj"]['purchase_quantity'] = purchase_dict['product_obj'].get('quantity')
            purchase_dict["product_obj"]['outbound_quantity'] = 0
            return_stock_list.append(purchase_dict.get("product_obj"))

    return return_stock_list


def cal_stock_list():
    """
    计算所有的产品的库存容量
    :return: 计算完毕之后的库存数据对象列表（包含入库数量、出库数量、剩余库存数量）
    """
    # 包含了去重合并
    all_purchase_product_list = cal_purchase_stock_list()
    all_outbound_product_list = cal_outbound_stock_list()
    return cal_stock(all_purchase_product_list, all_outbound_product_list)


def cal_purchase_stock_list():
    """
    计算入库产品的库存容量
    :return: 计算完毕之后的库存数据对象列表（包含入库数量、出库数量、剩余库存数量）
    """
    # 保存所有的入库产品数据（未去重合并）
    all_purchase_product_list = []

    # 获取所有的入库单
    purchase_obj_list = PurchaseOrder.query.all()
    for purchase_obj in purchase_obj_list:
        purchase_id = purchase_obj.business_id
        purchase_product_list = get_products_by_purchase_order_id(purchase_id)
        for _ in purchase_product_list.get("data"):
            all_purchase_product_list.append(_)

    # 去重合并，入库的所有产品的数量（瓶），出库所有产品的数量（瓶）
    duplicate_remove_purchase = duplicate_remove_purchase_product(purchase_product_list=all_purchase_product_list)
    return duplicate_remove_purchase


def cal_outbound_stock_list():
    """
    计算出库产品的库存容量
    :return: 计算完毕之后的库存数据对象列表（包含入库数量、出库数量、剩余库存数量）
    """
    # 保存所有的出库产品数据（未去重合并）
    all_outbound_product_list = []

    outbound_obj_list = OutboundOrder.query.all()
    for outbound_obj in outbound_obj_list:
        outbound_id = outbound_obj.business_id
        outbound_product_list = get_products_by_outbound_order_id(outbound_id)
        for _ in outbound_product_list.get("data"):
            all_outbound_product_list.append(_)

    # 去重合并，入库的所有产品的数量（瓶），出库所有产品的数量（瓶）
    duplicate_remove_outbound = duplicate_remove_outbound_product(outbound_product_list=all_outbound_product_list)
    return duplicate_remove_outbound


def get_total_purchase_price():
    """
    获取入库单的金额总和
    :return:
    """
    return db.session.query(func.sum(PurchaseOrder.total_price)).scalar()


def get_purchase_statistic():
    """
    获取入库单的金额统计信息
    :return:
    """
    return PurchaseOrder.query.order_by(PurchaseOrder.create_time.asc()).all()


def get_outbound_pie_statistic():
    """
    获取各个经销商的出库单的销售额饼图统计信息
    :return:
    """
    return db.session.query(OutboundOrder.belong_to, func.sum(OutboundOrder.total_price).label('sum')).group_by(
        OutboundOrder.belong_to).order_by(desc('sum')).limit(5).all()


def get_outbound_transaction_statistic():
    """
    获取各个经销商的出库单的交易额统计信息
    :return:
    """
    return db.session.query(OutboundOrder.belong_to, func.sum(OutboundOrder.total_price).label('sum')).group_by(
        OutboundOrder.belong_to).order_by(desc('sum')).all()


def get_product_transaction_statistic():
    """
    获取各个产品的交易额统计信息
    :return:
    """
    # 所有的出库产品列表（未去重合并产品）
    all_product_list = []
    # 所有的出库订单列表
    outbound_list = OutboundOrder.query.all()
    for outbound_obj in outbound_list:
        outbound_id = outbound_obj.business_id
        # 查询该出库订单所包含的产品列表
        product_list = OutboundOrderList.query.filter_by(outbound_order_id=outbound_id).all()
        for product_obj in product_list:
            dealer_product_id = product_obj.dealer_product_id
            dealer_product = DealerProductList.query.filter_by(business_id=dealer_product_id).first()
            # 精确的产品
            product = ProductList.query.filter_by(business_id=dealer_product.product_id).first()
            _dict = dealer_product.as_dict()
            _dict['product_name'] = product.product_name
            _dict['specifications'] = product.specifications
            _dict['quantity'] = product_obj.quantity
            all_product_list.append(_dict)

    # 合并所有产品数据（未去重）
    merge_product = {}
    # 先把key加上（初始化）
    for product_obj in all_product_list:
        merge_product[product_obj.get("product_name")] = []
    for product_obj in all_product_list:
        merge_product[product_obj.get("product_name")].append(product_obj)

    # 根据产品名进行合并去重（已合并的产品）
    merge_dict = remove_duplicate_product(data_list=merge_product)

    return_list = []
    # 初始化values的key
    for product_name, product_obj_list in merge_dict.items():
        return_product_dict = {
            "name": "",
            "outbound_price": 0
        }
        for product_obj in product_obj_list:
            _product_name = "{}({}ML)".format(product_obj.get("product_name"), product_obj.get('specifications'))
            return_product_dict['name'] = _product_name
            count_price = product_obj.get('quantity') * product_obj.get('unit_price')
            return_product_dict['outbound_price'] = float("{:.2f}".format(count_price))
        return_list.append(return_product_dict)

    # 排序（从大到小 ）
    def _bubble_sort(arr):
        """
        冒泡排序
        :param arr:
        :return:
        """
        n = len(arr)
        # 遍历所有数组元素
        for i in range(n):
            # Last i elements are already in place
            for j in range(0, n - i - 1):
                if arr[j]['outbound_price'] > arr[j + 1]['outbound_price']:
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]

    _bubble_sort(return_list)
    return_list.reverse()
    return return_list


def remove_duplicate_dealer_product(data_list):
    """
    合并经销商产品（进行去重，根据经销商名字来进行去重合并）
    :param data_list:
    :return:
    """
    # 去重合并产品的数量
    merge_dict = {}
    for key, values in data_list.items():
        # 每个经销的产品进行merge
        merge_data_list = []
        for index, product_obj in enumerate(values):
            value_tuple = (product_obj.get('product_name'), product_obj.get('specifications'))

            # 如果暂存的列表里有数据
            if merge_data_list:
                is_exist = False
                for _product_obj in merge_data_list:
                    _value_tuple = (
                        _product_obj.get('product_name'), _product_obj.get('specifications')
                    )
                    if value_tuple == _value_tuple:
                        is_exist = True
                        # 如果存在，现有的加上暂存的 _product_obj.get('quantity') 数量
                        _product_obj['quantity'] = _product_obj['quantity'] + product_obj['quantity']
                        break
                if not is_exist:
                    merge_data_list.append(product_obj)
            else:
                merge_data_list.append(product_obj)
        merge_dict[key] = merge_data_list
    return merge_dict


def remove_duplicate_product(data_list):
    """
    合并产品（进行去重，根据产品来去重合并）
    :param data_list:
    :return:
    """
    # 去重合并产品的数量
    merge_dict = {}
    for key, values in data_list.items():
        # 每个经销的产品进行merge
        merge_data_list = []
        for index, product_obj in enumerate(values):
            value_tuple = (product_obj.get('product_name'), product_obj.get('specifications'))

            # 如果暂存的列表里有数据
            if merge_data_list:
                is_exist = False
                for _product_obj in merge_data_list:
                    _value_tuple = (
                        _product_obj.get('product_name'), _product_obj.get('specifications')
                    )
                    if value_tuple == _value_tuple:
                        is_exist = True
                        # 如果存在，现有的加上暂存的 _product_obj.get('quantity') 数量
                        _product_obj['quantity'] = _product_obj['quantity'] + product_obj['quantity']
                        break
                if not is_exist:
                    merge_data_list.append(product_obj)
            else:
                merge_data_list.append(product_obj)
        merge_dict[key] = merge_data_list
    return merge_dict


def get_outbound_bar_statistic():
    """
    获取各个经销商的出库单的销售额 柱状图 统计信息
    :return:
    """
    data_list = []
    outbound_list = OutboundOrder.query.all()
    for outbound_obj in outbound_list:
        outbound_id = outbound_obj.business_id
        product_list = OutboundOrderList.query.filter_by(outbound_order_id=outbound_id).all()
        for product_obj in product_list:
            dealer_product_id = product_obj.dealer_product_id
            dealer_product = DealerProductList.query.filter_by(business_id=dealer_product_id).first()
            product = ProductList.query.filter_by(business_id=dealer_product.product_id).first()
            _dict = dealer_product.as_dict()
            _dict['product_name'] = product.product_name
            _dict['specifications'] = product.specifications
            _dict['quantity'] = product_obj.quantity
            data_list.append(_dict)

    # 合并经销商的所有产品数据（未去重）
    merge_dealer = {}
    # 先把key加上（初始化）
    for product_obj in data_list:
        merge_dealer[product_obj.get("belong_to")] = []
    for product_obj in data_list:
        merge_dealer[product_obj.get("belong_to")].append(product_obj)

    # 经销商产品去重（已合并的经销商产品）
    merge_dict = remove_duplicate_dealer_product(data_list=merge_dealer)

    # 根据各个产品进行分类，例如（香型进行统一）：
    # keys = ["精品老白干", "简约光瓶"]
    # {
    #   "同事朋友": [10000, 50000],
    #   "餐饮": [50000, 150000]
    # }
    return_product_dict = {
        "keys": set(),
        "values": {}
    }
    # 初始化values的key
    for dealer_name, product_obj_list in merge_dict.items():
        for product_obj in product_obj_list:
            return_product_dict['values'][dealer_name] = []
            _product_name = "{}({}ML)".format(product_obj.get("product_name"), product_obj.get('specifications'))
            return_product_dict['keys'].add(
                "{}({}ML)".format(product_obj.get("product_name"), product_obj.get('specifications'))
            )
    return_product_dict['keys'] = list(return_product_dict.get('keys'))
    # keys顺序循环获取各个经销商的产品数据
    for product_name in return_product_dict['keys']:
        for dealer_name, product_obj_list in merge_dict.items():
            is_exist = False
            for product_obj in product_obj_list:
                _product_name = "{}({}ML)".format(product_obj.get("product_name"), product_obj.get('specifications'))

                if _product_name == product_name:
                    is_exist = True
                    return_product_dict['values'][dealer_name].append(product_obj.get('quantity'))
                    break
            if not is_exist:
                return_product_dict['values'][dealer_name].append(0)

    return return_product_dict


def get_outbound_statistic():
    """
    获出库单的金额统计信息
    :return:
    """
    return OutboundOrder.query.order_by(OutboundOrder.create_time.asc()).all()


def get_total_purchase_piece():
    """
    获取入库单的数量总和
    :return:
    """
    return db.session.query(func.sum(PurchaseOrder.total_piece)).scalar()


def get_total_outbound_price():
    """
    获取出库单的金额总和
    :return:
    """
    return db.session.query(func.sum(OutboundOrder.total_price)).scalar()


def get_total_outbound_piece():
    """
    获取出库单的数量总和
    :return:
    """
    return db.session.query(func.sum(OutboundOrder.total_piece)).scalar()


def get_purchase_order_limit(page: int = 0, limit: int = 100):
    """
    获取订货单数据列表
    :param page: 当前页
    :param limit: 每页多少条数据
    :return:
    """
    result_list = PurchaseOrder.query.order_by(PurchaseOrder.create_time.desc()).offset(page).limit(limit).all()
    return {"data": result_list, "count": PurchaseOrder.query.count()}


def add_purchase_order(data: dict):
    """
    新增订货单
    :param data: 数据字典
    :return:
    """
    try:
        purchase_order_obj = PurchaseOrder(**data)
        db.session.add(purchase_order_obj)
        db.session.commit()
        # db.session.flush()
        return purchase_order_obj
    except:
        db.session.rollback()
        raise AddPurchaseException


def get_products_by_purchase_order_id(data_id):
    """
    通过入库单id 获取 入库单产品的所有列表
    :param data_id: 入库单id
    :return:
    """
    A = aliased(PurchaseOrderList)
    B = aliased(ProductList)
    result_tuple_list = db.session.query(A, B).join(B, A.product_id == B.business_id).filter(
        A.purchase_order_id == data_id).all()
    result_list = format_purchase_product(data_list=result_tuple_list)
    return {"data": result_list, "count": PurchaseOrderList.query.filter_by(purchase_order_id=data_id).count()}


def del_purchase_order_by_id(data_id):
    """
    通过入库单id 删除该次采购订单，并且将采购的商品全部删除
    :param data_id: 订单id
    :return:
    """
    # 1. 删除所有的入库产品
    try:
        PurchaseOrderList.query.filter(PurchaseOrderList.purchase_order_id == data_id).delete()
        db.session.commit()
    except:
        db.session.rollback()
        raise DeletePurchaseProductListException

    # 2. 删除订单
    try:
        PurchaseOrder.query.filter(PurchaseOrder.business_id == data_id).delete()
        db.session.commit()
    except:
        db.session.rollback()
        raise DeletePurchaseException


def del_purchase_product_by_id(data_id):
    """
    通过入库单id 删除该次入库的所有产品
    :param data_id: 订单id
    :return:
    """
    # 删除所有的入库产品
    try:
        PurchaseOrderList.query.filter(PurchaseOrderList.purchase_order_id == data_id).delete()
        db.session.commit()
    except:
        db.session.rollback()
        raise DeletePurchaseProductListException


def add_purchase_product(data: dict):
    """
    新增订购单的商品列表
    :param data: 数据字典
    :return:
    """
    try:
        purchase_order_obj = PurchaseOrderList(**data)
        db.session.add(purchase_order_obj)
        db.session.commit()
        # db.session.flush()
        return purchase_order_obj
    except:
        db.session.rollback()
        raise AddPurchaseProductException


def get_outbound_order_limit(dealer_name, page: int = 0, limit: int = 100):
    """
    获取出库单数据列表（也可以根据经销商名字进行过滤）
    :param dealer_name: 根据经销商名过滤
    :param page: 当前页
    :param limit: 每页多少条数据
    :return:
    """
    if dealer_name:
        result_list = OutboundOrder.query.filter(OutboundOrder.belong_to.like('%{}%'.format(dealer_name))).order_by(
            OutboundOrder.create_time.desc()).offset(page).limit(limit).all()
        return {
            "data": result_list,
            "count": OutboundOrder.query.filter_by(belong_to=dealer_name).count()
        }
    else:
        result_list = OutboundOrder.query.order_by(OutboundOrder.create_time.desc()).offset(page).limit(limit).all()
        return {"data": result_list, "count": OutboundOrder.query.count()}


def add_outbound_order(data: dict):
    """
    新增出库单
    :param data: 数据字典
    :return:
    """
    try:
        outbound_obj = OutboundOrder(**data)
        db.session.add(outbound_obj)
        db.session.commit()
        # db.session.flush()
        return outbound_obj
    except:
        db.session.rollback()
        raise AddOutboundException


def update_outbound_by_business_id(data_id: str, data):
    """
    根据 业务id 更新出库单
    :param data_id:
    :param data:
    :return:
    """
    try:
        # 根据业务id查询这条数据
        outbound_order_obj = OutboundOrder.query.filter_by(business_id=data_id).first()
        if outbound_order_obj:
            # 执行更新操作
            OutboundOrder.query.filter(OutboundOrder.business_id == data_id).update(data)
            db.session.commit()
        else:
            raise UpdateOutboundException
    except:
        db.session.rollback()
        raise UpdateOutboundException


def update_purchase_by_business_id(data_id: str, data):
    """
    根据 业务id 更新入库单
    :param data_id:
    :param data:
    :return:
    """
    try:
        # 根据业务id查询这条数据
        purchase_order_obj = PurchaseOrder.query.filter_by(business_id=data_id).first()
        if purchase_order_obj:
            # 执行更新操作
            PurchaseOrder.query.filter(PurchaseOrder.business_id == data_id).update(data)
            db.session.commit()
        else:
            raise UpdatePurchaseException
    except:
        db.session.rollback()
        raise UpdatePurchaseException


def get_products_by_outbound_order_id(data_id):
    """
    通过出库单ID 获取 出库单产品的所有列表
    :param data_id: 出库单id
    :return:
    """
    A = aliased(OutboundOrderList)
    B = aliased(DealerProductList)
    C = aliased(ProductList)

    result_tuple_list = db.session.query(A, C).join(B, A.dealer_product_id == B.business_id).join(
        C, B.product_id == C.business_id).filter(A.outbound_order_id == data_id).all()
    result_list = format_outbound_product(data_list=result_tuple_list)
    return {"data": result_list, "count": OutboundOrderList.query.filter_by(outbound_order_id=data_id).count()}


def get_products_by_dealer_product_id(dealer_product_id):
    """
    通过 经销商产品id 获取 产品的基础信息，例如 每件多少瓶、什么规格、什么香型。
    :param dealer_product_id: 经销商产品id
    :return:
    """
    return DealerProductList.query.filter_by(business_id=dealer_product_id).first()


def del_outbound_order_product(data_id):
    """
    通过出库单ID 删除该次出库单的所有关联商品
    :param data_id: 出库单id
    :return:
    """
    # 1. 删除所有的订购产品
    try:
        OutboundOrderList.query.filter(OutboundOrderList.outbound_order_id == data_id).delete()
        db.session.commit()
    except:
        db.session.rollback()
        raise DeleteOutboundProductListException


def del_outbound_order_by_id(data_id):
    """
    通过出库单ID 删除该次出库单，并且将出库的商品全部删除
    :param data_id: 出库单id
    :return:
    """
    # 1. 删除所有的订购产品
    try:
        OutboundOrderList.query.filter(OutboundOrderList.outbound_order_id == data_id).delete()
        db.session.commit()
    except:
        db.session.rollback()
        raise DeleteOutboundProductListException

    # 2. 删除订单
    try:
        OutboundOrder.query.filter(OutboundOrder.business_id == data_id).delete()
        db.session.commit()
    except:
        db.session.rollback()
        raise DeleteOutboundException


def add_outbound_product(data: dict):
    """
    新增出库单的商品列表
    :param data: 数据字典
    :return:
    """
    try:
        outbound_obj = OutboundOrderList(**data)
        db.session.add(outbound_obj)
        db.session.commit()
        # db.session.flush()
        return outbound_obj
    except:
        db.session.rollback()
        raise AddOutboundProductException

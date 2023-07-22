from utils.date_utils import time_to_timestamp


def format_purchase_product(data_list):
    """
    处理入库产品数据的方法，将返回的 tuple 结果进行格式化json
    :param data_list: 接收搜索返回的数据（tuple类型，第一列是 PurchaseOrderList 数据类型，第二列是 ProductList 数据类型）
    :return:
    """
    return_data_list = []
    for purchase_order_obj, product_obj in data_list:
        # json格式化
        purchase_order_dict = purchase_order_obj.as_dict()
        # 添加几个列名
        purchase_order_dict['product_name'] = product_obj.product_name
        purchase_order_dict['specifications'] = product_obj.specifications
        purchase_order_dict['scent_type'] = product_obj.scent_type
        purchase_order_dict['specification_of_piece'] = product_obj.specification_of_piece
        purchase_order_dict['unit_price'] = product_obj.unit_price
        purchase_order_dict['img_url'] = product_obj.img_url
        purchase_order_dict['thumb_img_url'] = product_obj.thumb_img_url
        return_data_list.append(purchase_order_dict)

    # 统一转换成时间戳的形式
    return time_to_timestamp(return_data_list)


def format_outbound_product(data_list):
    """
    处理出库产品数据的方法，将返回的 tuple 结果进行格式化json
    :param data_list: 接收搜索返回的数据（tuple类型，第一列是 OutboundOrderList 数据类型，第二列是 ProductList 数据类型）
    :return:
    """
    return_data_list = []
    for outbound_order_obj, product_obj in data_list:
        # json格式化
        outbound_order_dict = outbound_order_obj.as_dict()
        # 添加几个列名
        outbound_order_dict['product_name'] = product_obj.product_name
        outbound_order_dict['specifications'] = product_obj.specifications
        outbound_order_dict['scent_type'] = product_obj.scent_type
        outbound_order_dict['specification_of_piece'] = product_obj.specification_of_piece
        outbound_order_dict['img_url'] = product_obj.img_url
        outbound_order_dict['thumb_img_url'] = product_obj.thumb_img_url
        return_data_list.append(outbound_order_dict)

    # 统一转换成时间戳的形式
    return time_to_timestamp(return_data_list)


def search_stock_product(data_list, search_name):
    """
    按产品名称搜索数据（进行模糊匹配）
    :param data_list:
    :param search_name:
    :return:
    """
    return_search_data_list = []
    if search_name:
        for return_data_obj in data_list:
            if search_name in return_data_obj.get('product_name'):
                return_search_data_list.append(return_data_obj)
    else:
        return_search_data_list = data_list
    return return_search_data_list


def order_stock_data_list(data_list):
    """
    采用冒泡排序对 stock 数据按数量进行从大到小排序
    :param data_list:
    :return:
    """
    for i in range(len(data_list) - 1):
        # 记录最小数的索引
        minIndex = i
        for j in range(i + 1, len(data_list)):
            if data_list[j].get("quantity") < data_list[minIndex].get("quantity"):
                minIndex = j
        # i 不是最小数时，将 i 和最小数进行交换
        if i != minIndex:
            data_list[i], data_list[minIndex] = data_list[minIndex], data_list[i]

    # 从大到小排序
    data_list.reverse()
    return data_list

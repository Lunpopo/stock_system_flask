import time

from sqlalchemy import func, desc

from app_router.models.database import db
from app_router.models.stock_models import StockList, TransactionList
from exceptions.stock_exception import *


# 获取各个股票的盈利饼图信息
def get_profit_pie_statistic():
    """
    获取各个股票的盈利饼图信息
    :return:
    """
    return db.session.query(TransactionList.stock_id, func.sum(TransactionList.profit_amount).label('sum')).group_by(
        TransactionList.stock_id).order_by(desc('sum')).limit(10).all()


# 获取股票统计信息列表
def get_stock_list_limit(page: int = 0, limit: int = 100):
    """
    获取股票统计信息列表
    :param page: 当前页
    :param limit: 每页多少条数据
    :return:
    """
    result_list = StockList.query.order_by(StockList.create_time.desc()).offset(page).limit(limit).all()
    return {"data": result_list, "count": StockList.query.count()}


# 获取股票统计信息列表
def get_stock_list():
    """
    获取股票统计信息列表
    :return:
    """
    return StockList.query.all()


# 更新股票交易信息（一次更新一条）
def update_transaction_info(transaction_dict):
    """
    更新股票交易信息（一次更新一条）
    :param transaction_dict:
    :return:
    """
    try:
        transaction_id = transaction_dict['business_id']
        with db.session.begin_nested():
            # 1. 根据业务id查询这条数据
            transaction_obj = TransactionList.query.filter_by(business_id=transaction_id).first()
            if transaction_obj:
                # 执行更新操作
                TransactionList.query.filter(TransactionList.business_id == transaction_id).update(transaction_dict)
                db.session.flush()
            else:
                raise TransactinoNotExist
        db.session.commit()
    except:
        db.session.rollback()
        raise UpdateTransactinoException


# 通过 transaction_list 表的 business_id 获取股票交易信息
def get_transaction_info_by_id(data_id):
    """
    通过 transaction_list 表的 business_id 获取股票交易信息
    :param data_id:
    :return:
    """
    try:
        return TransactionList.query.filter_by(business_id=data_id).first()
    except:
        raise UpdateTransactinoException


# 更新股票 和 股票交易表
def update_stock_transaction_list(stock_dict, transaction_dict_list):
    """
    更新股票 和 股票交易表
    :param stock_dict:
    :param transaction_dict_list:
    :return:
    """
    try:
        stock_id = stock_dict['business_id']
        with db.session.begin_nested():
            # 1. 根据业务id查询这条数据
            stock_obj = StockList.query.filter_by(business_id=stock_id).first()
            if stock_obj:
                # 执行更新操作
                StockList.query.filter(StockList.business_id == stock_id).update(stock_dict)
                db.session.flush()
            else:
                raise UpdateStockListException

            # 2. 删除该股票的所有的交易信息
            TransactionList.query.filter(TransactionList.stock_id == stock_id).delete()
            db.session.flush()

            # 3. 添加最新的交易列表
            for _ in transaction_dict_list:
                _['stock_id'] = stock_id
                # 将 create_time 改为时间戳
                create_time = int(int(_['create_time']) / 1000)
                create_time_array = time.localtime(create_time)
                create_time = time.strftime("%Y-%m-%d %H:%M:%S", create_time_array)
                _['create_time'] = create_time
                # 将 update_time 改为时间戳
                update_time = int(int(_['update_time']) / 1000)
                update_time_array = time.localtime(update_time)
                update_time = time.strftime("%Y-%m-%d %H:%M:%S", update_time_array)
                _['update_time'] = update_time

            transaction_obj_list = [TransactionList(**_) for _ in transaction_dict_list]
            db.session.add_all(transaction_obj_list)
            db.session.flush()
        db.session.commit()
    except:
        db.session.rollback()
        raise UpdateStockTransactionException


# 新增股票列表
def add_stock_list(stock_list_data: dict, stock_transaction_list_data: dict):
    """
    新增股票列表
    :param stock_list_data:
    :param stock_transaction_list_data:
    :return:
    """
    try:
        with db.session.begin_nested():
            stock_list_obj = StockList(**stock_list_data)
            db.session.add(stock_list_obj)
            db.session.flush()
            stock_id = stock_list_obj.business_id
            for _ in stock_transaction_list_data:
                _['stock_id'] = stock_id
                # create_time
                create_time = int(int(_['create_time']) / 1000)
                create_time_array = time.localtime(create_time)
                create_time = time.strftime("%Y-%m-%d %H:%M:%S", create_time_array)
                _['create_time'] = create_time
                # update_time
                update_time = int(int(_['update_time']) / 1000)
                update_time_array = time.localtime(update_time)
                update_time = time.strftime("%Y-%m-%d %H:%M:%S", update_time_array)
                _['update_time'] = update_time

            stock_transaction_objs = [TransactionList(**_) for _ in stock_transaction_list_data]
            db.session.add_all(stock_transaction_objs)
            db.session.flush()
        db.session.commit()
    except:
        db.session.rollback()
        raise AddStockListException


# 通过 stock id 删除该股票及其所有的股票交易
def del_stock_by_id(data_id):
    """
    通过 stock id 删除该股票及其所有的股票交易
    :param data_id: stock id
    :return:
    """
    try:
        with db.session.begin_nested():
            # 1. 先删除该股票下的所有的交易
            TransactionList.query.filter(TransactionList.stock_id == data_id).delete()
            db.session.flush()
            # 2. 再删除该股票
            StockList.query.filter(StockList.business_id == data_id).delete()
            db.session.flush()
        db.session.commit()
    except:
        db.session.rollback()
        raise DelStockException


# 通过stock id 获取股票信息
def get_stock_info_by_id(data_id):
    """
    通过stock id 获取股票信息
    :param data_id: 入库单id
    :return:
    """
    # 该 股票id 的所有交易列表
    transaction_obj_list = TransactionList.query.filter_by(stock_id=data_id).order_by(
        TransactionList.create_time.asc()).all()
    stock_obj = StockList.query.filter_by(business_id=data_id).first()
    return {"transaction_obj_list": transaction_obj_list, "stock_obj": stock_obj}


# 通过stock id 获取股票
def get_stock_by_id(data_id):
    """
    通过stock id 获取股票
    :param data_id: 入库单id
    :return:
    """
    return StockList.query.filter_by(business_id=data_id).order_by(StockList.create_time.asc()).first()


# 通过stock id 获取所有的交易信息
def get_transaction_by_stock_id(data_id):
    """
    通过stock id 获取所有的交易信息
    :param data_id: stock id
    :return:
    """
    result_list = TransactionList.query.filter_by(stock_id=data_id).order_by(TransactionList.create_time.asc()).all()
    return {"data": result_list, "count": TransactionList.query.filter_by(stock_id=data_id).count()}


# 通过stock id 获取该股票未清仓的交易信息
def get_unclear_transaction_by_stock_id(data_id):
    """
    通过stock id 获取该股票未清仓的交易信息
    :param data_id: stock id
    :return:
    """
    result_list = TransactionList.query.filter_by(stock_id=data_id, transaction_status='未清仓').order_by(
        TransactionList.create_time.asc()).all()
    return result_list


# 通过 stock id 删除该股票的所有交易列表
def del_transaction_by_id(data_id):
    """
    通过 stock id 删除该股票的所有交易列表
    :param data_id: 订单id
    :return:
    """
    # 删除所有的入库产品
    try:
        TransactionList.query.filter(TransactionList.stock_id == data_id).delete()
        db.session.commit()
    except:
        db.session.rollback()
        raise DeleteTransactionException


# 根据 业务id 更新股票 stock_list 表
def update_stock_list_by_id(data_id: str, data):
    """
    根据 业务id 更新 stock_list 表
    :param data_id:
    :param data:
    :return:
    """
    try:
        # 根据业务id查询这条数据
        stock_obj = StockList.query.filter_by(business_id=data_id).first()
        if stock_obj:
            # 执行更新操作
            StockList.query.filter(StockList.business_id == data_id).update(data)
            db.session.commit()
        else:
            raise UpdateStockListException
    except:
        db.session.rollback()
        raise UpdateStockListException

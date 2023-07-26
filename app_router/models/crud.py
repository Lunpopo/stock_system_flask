from sqlalchemy import asc, desc
from sqlalchemy.orm import aliased

from app_router.models.data_models import ProductList, DealerProductList, DealerList
from app_router.models.database import db
from enums.enums import OrderNameEnum
from exceptions.product_exception import *

A = aliased(DealerProductList)  # 别名
B = aliased(ProductList)


def get_product_list_limit(page: int = 0, limit: int = 100, order_by='-update_time'):
    """
    获取产品列表-用于表格数据
    :param page: 当前页
    :param limit: 每页多少条数据
    :param order_by: 排序，例如："+product_name"
    :return:
    """
    if order_by and order_by.startswith('-'):
        # 降序
        order_name = order_by.split("-")[-1]
        if order_name in OrderNameEnum.__members__:
            # 传入的 order_name 在枚举里面
            result_list = ProductList.query.order_by(desc(order_name)).offset(page).limit(limit).all()
        else:
            # 传入的 order_name 不在枚举里面，不知道的类别就用 update_time 排序
            result_list = ProductList.query.order_by(desc('update_time')).offset(page).limit(limit).all()

    elif order_by and order_by.startswith('+'):
        # 升序
        order_name = order_by.split("+")[-1]
        if order_name in OrderNameEnum.__members__:
            result_list = ProductList.query.order_by(asc(order_name)).offset(page).limit(limit).all()
        else:
            # 不知道的类别就用 update_time 排序
            result_list = ProductList.query.order_by(asc('update_time')).offset(page).limit(limit).all()

    else:
        # 不知道用的什么
        result_list = ProductList.query.order_by(desc('update_time')).offset(page).limit(limit).all()

    return {"data": result_list, "count": ProductList.query.count()}


def get_all_product(order_by='-update_time'):
    """
    获取所有的产品列表-用于下载excel
    :param order_by: 排序，例如："+product_name"
    :return:
    """
    if order_by and order_by.startswith('-'):
        # 降序
        order_name = order_by.split("-")[-1]
        if order_name in OrderNameEnum.__members__:
            result_list = ProductList.query.order_by(desc(order_name)).all()
        else:
            # 不知道的类别就用 update_time 排序
            result_list = ProductList.query.order_by(desc('update_time')).all()

    elif order_by and order_by.startswith('+'):
        # 升序
        order_name = order_by.split("+")[-1]
        if order_name in OrderNameEnum.__members__:
            result_list = ProductList.query.order_by(asc(order_name)).all()
        else:
            # 不知道的类别就用 update_time 排序
            result_list = ProductList.query.order_by(asc('update_time')).all()

    else:
        # 不知道用的什么
        result_list = ProductList.query.order_by(desc('update_time')).all()

    return {"data": result_list, "count": ProductList.query.count()}


def get_all_dealer_product(product_name, dealer_name, order_by='-update_time'):
    """
    获取所有的产品列表-用于下载excel
    :param product_name: 搜索的关键字
    :param dealer_name: 经销商名字
    :param order_by: 排序，例如："+product_name"
    :return:
    """
    if product_name:
        if dealer_name:
            if order_by and order_by.startswith('-'):
                # 降序
                order_name = order_by.split("-")[-1]
                if order_name in OrderNameEnum.__members__:
                    result_tuple = db.session.query(A, B).join(B, A.product_id == B.business_id).filter(
                        A.belong_to == dealer_name).filter(B.product_name.like('%{}%'.format(product_name))).order_by(
                        desc(order_name)).all()
                else:
                    # 不在enum里面的就用 update_time 降序
                    result_tuple = db.session.query(A, B).join(B, A.product_id == B.business_id).filter(
                        A.belong_to == dealer_name).filter(B.product_name.like('%{}%'.format(product_name))).order_by(
                        desc(A.update_time)).all()

            elif order_by and order_by.startswith('+'):
                # 升序
                order_name = order_by.split("+")[-1]
                if order_name in OrderNameEnum.__members__:
                    result_tuple = db.session.query(A, B).join(B, A.product_id == B.business_id).filter(
                        A.belong_to == dealer_name).filter(B.product_name.like('%{}%'.format(product_name))).order_by(
                        asc(order_name)).all()
                else:
                    # 不在enum里面的就用 update_time 降序
                    result_tuple = db.session.query(A, B).join(B, A.product_id == B.business_id).filter(
                        A.belong_to == dealer_name).filter(B.product_name.like('%{}%'.format(product_name))).order_by(
                        asc(A.update_time)).all()

            else:
                result_tuple = db.session.query(A, B).join(B, A.product_id == B.business_id).filter(
                    A.belong_to == dealer_name).filter(B.product_name.like('%{}%'.format(product_name))).order_by(
                    desc(A.update_time)).all()

            return {
                "data": result_tuple,
                "count": db.session.query(A, B).join(B, A.product_id == B.business_id).filter(
                    A.belong_to == dealer_name).filter(B.product_name.like('%{}%'.format(product_name))).count()
            }

        else:
            if order_by and order_by.startswith('-'):
                # 降序
                order_name = order_by.split("-")[-1]
                if order_name in OrderNameEnum.__members__:
                    result_tuple = db.session.query(A, B).join(B, A.product_id == B.business_id).filter(
                        B.product_name.like('%{}%'.format(product_name))).order_by(desc(order_name)).all()
                else:
                    # 不在enum里面的就用 update_time 降序
                    result_tuple = db.session.query(A, B).join(B, A.product_id == B.business_id).filter(
                        B.product_name.like('%{}%'.format(product_name))).order_by(desc(A.update)).all()

            elif order_by and order_by.startswith('+'):
                # 降序
                order_name = order_by.split("+")[-1]
                if order_name in OrderNameEnum.__members__:
                    result_tuple = db.session.query(A, B).join(B, A.product_id == B.business_id).filter(
                        B.product_name.like('%{}%'.format(product_name))).order_by(asc(order_name)).all()
                else:
                    # 不在enum里面的就用 update_time 降序
                    result_tuple = db.session.query(A, B).join(B, A.product_id == B.business_id).filter(
                        B.product_name.like('%{}%'.format(product_name))).order_by(asc(A.update_time)).all()

            else:
                result_tuple = db.session.query(A, B).join(B, A.product_id == B.business_id).filter(
                    B.product_name.like('%{}%'.format(product_name))).order_by(desc(A.update_time)).all()

            return {
                "data": result_tuple,
                "count": db.session.query(A, B).join(B, A.product_id == B.business_id).filter(
                    B.product_name.like('%{}%'.format(product_name))).count()
            }

    else:
        if dealer_name:
            if order_by and order_by.startswith('-'):
                # 降序
                order_name = order_by.split("-")[-1]
                if order_name in OrderNameEnum.__members__:
                    result_tuple = db.session.query(A, B).join(B, A.product_id == B.business_id).filter(
                        A.belong_to == dealer_name).order_by(desc(order_name)).all()
                else:
                    result_tuple = db.session.query(A, B).join(B, A.product_id == B.business_id).filter(
                        A.belong_to == dealer_name).order_by(desc(A.update_time)).all()
            elif order_by and order_by.startswith('+'):
                # 降序
                order_name = order_by.split("+")[-1]
                if order_name in OrderNameEnum.__members__:
                    result_tuple = db.session.query(A, B).join(B, A.product_id == B.business_id).filter(
                        A.belong_to == dealer_name).order_by(asc(order_name)).all()
                else:
                    result_tuple = db.session.query(A, B).join(B, A.product_id == B.business_id).filter(
                        A.belong_to == dealer_name).order_by(asc(A.update_time)).all()
            else:
                result_tuple = db.session.query(A, B).join(B, A.product_id == B.business_id).filter(
                    A.belong_to == dealer_name).order_by(desc(A.update_time)).all()

            return {
                "data": result_tuple,
                "count": DealerProductList.query.filter_by(belong_to=dealer_name).count()
            }

        else:
            if order_by and order_by.startswith('-'):
                # 降序
                order_name = order_by.split("-")[-1]
                if order_name in OrderNameEnum.__members__:
                    result_tuple = db.session.query(A, B).join(B, A.product_id == B.business_id).order_by(
                        desc(order_name)).all()
                else:
                    result_tuple = db.session.query(A, B).join(B, A.product_id == B.business_id).order_by(
                        desc(A.update_time)).all()
            elif order_by and order_by.startswith('+'):
                # 升序
                order_name = order_by.split("+")[-1]
                if order_name in OrderNameEnum.__members__:
                    result_tuple = db.session.query(A, B).join(B, A.product_id == B.business_id).order_by(
                        asc(order_name)).all()
                else:
                    result_tuple = db.session.query(A, B).join(B, A.product_id == B.business_id).order_by(
                        asc(A.update_time)).all()
            else:
                result_tuple = db.session.query(A, B).join(B, A.product_id == B.business_id).order_by(
                    desc(A.update_time)).all()

            return {
                "data": result_tuple,
                "count": DealerProductList.query.count()
            }


def get_dealer_product_list_by_dealer_name(dealer_name: str, page: int = 0, limit: int = 100):
    """
    根据 经销商的名字过滤 获取产品列表
    :param dealer_name: 经销商的名字
    :param page: 当前页
    :param limit: 每页多少条数据
    :return:
    """
    result_list = DealerProductList.query.filter(DealerProductList.belong_to.like('%{}%'.format(dealer_name))) \
        .offset(page).limit(limit).all()
    return {
        "data": result_list,
        "count": DealerProductList.query.filter(DealerProductList.belong_to.like('%{}%'.format(dealer_name))).count()
    }


def get_all_dealer_product_list_by_dealer_name(dealer_name: str):
    """
    根据 经销商的名字 获取所有的产品列表
    :param dealer_name: 经销商的名字
    :param page: 当前页
    :param limit: 每页多少条数据
    :return:
    """
    result_list = DealerProductList.query.filter(DealerProductList.belong_to.like('%{}%'.format(dealer_name))).all()
    return {
        "data": result_list,
        "count": len(result_list)
    }


def get_dealer_list():
    """
    获取经销商名单列表
    :return:
    """
    result_list = DealerList.query.order_by(DealerList.create_time.desc()).all()
    return {"data": result_list, "count": DealerList.query.count()}


def search_dealer_list(dealer_name: str, page: int = 0, limit: int = 10, order_by="-update_time"):
    """
    搜索经销商名单列表，并且分页加排序
    :return:
    """
    if order_by and order_by.startswith('-'):
        # 降序
        order_name = order_by.split("-")[-1]

        if dealer_name:
            # 如果给出了 product_name 关键词
            if order_name in OrderNameEnum.__members__:
                result_list = DealerList.query.filter(DealerList.dealer_name.like('%{}%'.format(
                    dealer_name))).order_by(desc(order_name)).offset(page).limit(limit).all()
            else:
                # 不知道的类别就用 update_time 排序
                result_list = DealerList.query.filter(DealerList.dealer_name.like('%{}%'.format(
                    dealer_name))).order_by(desc('update_time')).offset(page).limit(limit).all()

            return {
                "data": result_list,
                "count": DealerList.query.filter(DealerList.dealer_name.like('%{}%'.format(dealer_name))).count()
            }

        else:
            # 搜索的时候没有给出 dealer_name，给出所有的数据
            if order_name in OrderNameEnum.__members__:
                result_list = DealerList.query.order_by(desc(order_name)).offset(page).limit(limit).all()
            else:
                # 不知道的类别就用 update_time 排序
                result_list = DealerList.query.order_by(desc('update_time')).offset(page).limit(limit).all()

            return {
                "data": result_list,
                "count": DealerList.query.count()
            }

    elif order_by and order_by.startswith('+'):
        # 升序
        order_name = order_by.split("+")[-1]

        if dealer_name:
            # 如果给出了 product_name 关键词
            if order_name in OrderNameEnum.__members__:
                result_list = DealerList.query.filter(DealerList.dealer_name.like('%{}%'.format(
                    dealer_name))).order_by(asc(order_name)).offset(page).limit(limit).all()
            else:
                # 不知道的类别就用 update_time 排序
                result_list = DealerList.query.filter(DealerList.dealer_name.like('%{}%'.format(
                    dealer_name))).order_by(asc('update_time')).offset(page).limit(limit).all()

            return {
                "data": result_list,
                "count": DealerList.query.filter(DealerList.dealer_name.like('%{}%'.format(
                    dealer_name))).count()
            }

        else:
            # 搜索的时候没有给出 product_name，给出所有的数据
            if order_name in OrderNameEnum.__members__:
                result_list = DealerList.query.order_by(asc(order_name)).offset(page).limit(limit).all()
            else:
                # 不知道的类别就用 update_time 排序
                result_list = DealerList.query.order_by(asc('update_time')).offset(page).limit(limit).all()
            return {
                "data": result_list,
                "count": DealerList.query.count()
            }

    else:
        # 不知道是什么，直接用 -update_time 进行排序
        if dealer_name:
            # 不知道的类别就用 update_time 排序
            result_list = DealerList.query.filter(DealerList.dealer_name.like('%{}%'.format(
                dealer_name))).order_by(desc('update_time')).offset(page).limit(limit).all()
            return {
                "data": result_list,
                "count": DealerList.query.filter(DealerList.dealer_name.like('%{}%'.format(dealer_name))).count()
            }

        else:
            result_list = DealerList.query.order_by(desc('update_time')).offset(page).limit(limit).all()
            return {"data": result_list, "count": DealerList.query.count()}


def search_product(product_name: str, page: int = 0, limit: int = 10, order_by="-update_time"):
    """
    搜索产品
    :param product_name: 产品名称
    :param page: 当前页
    :param limit: 每页多少条数据
    :param order_by: 排序，例如："+product_name"
    :return:
    """
    if order_by and order_by.startswith('-'):
        # 降序
        order_name = order_by.split("-")[-1]

        if product_name:
            # 如果给出了 product_name 关键词
            if order_name in OrderNameEnum.__members__:
                result_list = ProductList.query.filter(ProductList.product_name.like('%{}%'.format(
                    product_name))).order_by(desc(order_name)).offset(page).limit(limit).all()
            else:
                # 不知道的类别就用 update_time 排序
                result_list = ProductList.query.filter(
                    ProductList.product_name.like('%{}%'.format(product_name))
                ).order_by(desc('update_time')).offset(page).limit(limit).all()

            return {
                "data": result_list,
                "count": ProductList.query.filter(ProductList.product_name.like('%{}%'.format(product_name))).count()
            }

        else:
            # 搜索的时候没有给出 product_name，给出所有的数据
            if order_name in OrderNameEnum.__members__:
                result_list = ProductList.query.order_by(desc(order_name)).offset(page).limit(limit).all()
            else:
                # 不知道的类别就用 update_time 排序
                result_list = ProductList.query.order_by(desc('update_time')).offset(page).limit(limit).all()

            return {
                "data": result_list,
                "count": ProductList.query.count()
            }

    elif order_by and order_by.startswith('+'):
        # 升序
        order_name = order_by.split("+")[-1]

        if product_name:
            # 如果给出了 product_name 关键词
            if order_name in OrderNameEnum.__members__:
                result_list = ProductList.query.filter(ProductList.product_name.like('%{}%'.format(
                    product_name))).order_by(asc(order_name)).offset(page).limit(limit).all()
            else:
                # 不知道的类别就用 update_time 排序
                result_list = ProductList.query.filter(ProductList.product_name.like('%{}%'.format(
                    product_name))).order_by(asc('update_time')).offset(page).limit(limit).all()

            return {
                "data": result_list,
                "count": ProductList.query.filter(ProductList.product_name.like('%{}%'.format(
                    product_name))).count()
            }

        else:
            # 搜索的时候没有给出 product_name，给出所有的数据
            if order_name in OrderNameEnum.__members__:
                result_list = ProductList.query.order_by(asc(order_name)).offset(page).limit(limit).all()
            else:
                # 不知道的类别就用 update_time 排序
                result_list = ProductList.query.order_by(asc('update_time')).offset(page).limit(limit).all()
            return {
                "data": result_list,
                "count": ProductList.query.count()
            }

    else:
        # 不知道是什么，直接用 -update_time 进行排序
        if product_name:
            # 不知道的类别就用 update_time 排序
            result_list = ProductList.query.filter(ProductList.product_name.like('%{}%'.format(
                product_name))).order_by(desc('update_time')).offset(page).limit(limit).all()
            return {
                "data": result_list,
                "count": ProductList.query.filter(ProductList.product_name.like(
                    '%{}%'.format(product_name))).count()
            }

        else:
            result_list = ProductList.query.order_by(desc('update_time')).offset(page).limit(limit).all()
            return {"data": result_list, "count": ProductList.query.count()}


def search_dealer_product(title: str, dealer_name: str, page: int = 0, limit: int = 100, order_by='-update_time'):
    """
    搜索经销商产品
    :param title: 产品名称
    :param dealer_name: 经销商名称
    :param page: 当前页
    :param limit: 每页多少条数据
    :param order_by: 排序，例如："+product_name"
    :return:
    """
    if title:
        if dealer_name:
            if order_by and order_by.startswith('-'):
                # 降序
                order_name = order_by.split("-")[-1]
                if order_name in OrderNameEnum.__members__:
                    result_tuple = db.session.query(A, B).join(B, A.product_id == B.business_id).filter(
                        A.belong_to == dealer_name).filter(B.product_name.like('%{}%'.format(title))).order_by(
                        desc(order_name)).offset(page).limit(limit).all()
                else:
                    # 不在enum里面的就用 update_time 降序
                    result_tuple = db.session.query(A, B).join(B, A.product_id == B.business_id).filter(
                        A.belong_to == dealer_name).filter(B.product_name.like('%{}%'.format(title))).order_by(
                        desc(A.update_time)).offset(page).limit(limit).all()

            elif order_by and order_by.startswith('+'):
                # 升序
                order_name = order_by.split("+")[-1]
                if order_name in OrderNameEnum.__members__:
                    result_tuple = db.session.query(A, B).join(B, A.product_id == B.business_id).filter(
                        A.belong_to == dealer_name).filter(B.product_name.like('%{}%'.format(title))).order_by(
                        asc(order_name)).offset(page).limit(limit).all()
                else:
                    # 不在enum里面的就用 update_time 降序
                    result_tuple = db.session.query(A, B).join(B, A.product_id == B.business_id).filter(
                        A.belong_to == dealer_name).filter(B.product_name.like('%{}%'.format(title))).order_by(
                        asc(A.update_time)).offset(page).limit(limit).all()

            else:
                result_tuple = db.session.query(A, B).join(B, A.product_id == B.business_id).filter(
                    A.belong_to == dealer_name).filter(B.product_name.like('%{}%'.format(title))).order_by(
                    desc(A.update_time)).offset(page).limit(limit).all()

            return {
                "data": result_tuple,
                # 给出了 dealer_name 进行搜索
                "count": db.session.query(A, B).join(B, A.product_id == B.business_id).filter(
                    A.belong_to == dealer_name).filter(B.product_name.like('%{}%'.format(title))).count()
            }

        else:
            if order_by and order_by.startswith('-'):
                # 降序
                order_name = order_by.split("-")[-1]
                if order_name in OrderNameEnum.__members__:
                    result_tuple = db.session.query(A, B).join(B, A.product_id == B.business_id).filter(
                        B.product_name.like('%{}%'.format(title))).order_by(desc(order_name)).offset(page).limit(
                        limit).all()
                else:
                    # 不在enum里面的就用 update_time 降序
                    result_tuple = db.session.query(A, B).join(B, A.product_id == B.business_id).filter(
                        B.product_name.like('%{}%'.format(title))).order_by(desc(A.update_time)).offset(page).limit(
                        limit).all()

            elif order_by and order_by.startswith('+'):
                # 降序
                order_name = order_by.split("+")[-1]
                if order_name in OrderNameEnum.__members__:
                    result_tuple = db.session.query(A, B).join(B, A.product_id == B.business_id).filter(
                        B.product_name.like('%{}%'.format(title))).order_by(asc(order_name)).offset(page).limit(
                        limit).all()
                else:
                    # 不在enum里面的就用 update_time 降序
                    result_tuple = db.session.query(A, B).join(B, A.product_id == B.business_id).filter(
                        B.product_name.like('%{}%'.format(title))).order_by(asc(A.update_time)).offset(page).limit(
                        limit).all()

            else:
                result_tuple = db.session.query(A, B).join(B, A.product_id == B.business_id).filter(
                    B.product_name.like('%{}%'.format(title))).order_by(desc(A.update_time)).offset(page).limit(
                    limit).all()

            return {
                "data": result_tuple,
                # 没有给出 dealer_name 进行搜索
                "count": db.session.query(A, B).join(B, A.product_id == B.business_id).filter(
                    B.product_name.like('%{}%'.format(title))).count()
            }

    else:
        if dealer_name:
            if order_by and order_by.startswith('-'):
                # 降序
                order_name = order_by.split("-")[-1]
                if order_name in OrderNameEnum.__members__:
                    result_tuple = db.session.query(A, B).join(B, A.product_id == B.business_id).filter(
                        A.belong_to == dealer_name).order_by(desc(order_name)).offset(page).limit(limit).all()
                else:
                    result_tuple = db.session.query(A, B).join(B, A.product_id == B.business_id).filter(
                        A.belong_to == dealer_name).order_by(desc(A.update_time)).offset(page).limit(limit).all()
            elif order_by and order_by.startswith('+'):
                # 降序
                order_name = order_by.split("+")[-1]
                if order_name in OrderNameEnum.__members__:
                    result_tuple = db.session.query(A, B).join(B, A.product_id == B.business_id).filter(
                        A.belong_to == dealer_name).order_by(asc(order_name)).offset(page).limit(limit).all()
                else:
                    result_tuple = db.session.query(A, B).join(B, A.product_id == B.business_id).filter(
                        A.belong_to == dealer_name).order_by(asc(A.update_time)).offset(page).limit(limit).all()

            else:
                result_tuple = db.session.query(A, B).join(B, A.product_id == B.business_id).filter(
                    A.belong_to == dealer_name).order_by(desc(A.update_time)).offset(page).limit(limit).all()

            return {
                "data": result_tuple,
                "count": DealerProductList.query.filter_by(belong_to=dealer_name).count()
            }

        else:
            if order_by and order_by.startswith('-'):
                # 降序
                order_name = order_by.split("-")[-1]
                if order_name in OrderNameEnum.__members__:
                    result_tuple = db.session.query(A, B).join(B, A.product_id == B.business_id).filter(
                        A.belong_to == dealer_name).order_by(desc(order_name)).offset(page).limit(limit).all()
                else:
                    result_tuple = db.session.query(A, B).join(B, A.product_id == B.business_id).filter(
                        A.belong_to == dealer_name).order_by(desc(A.update_time)).offset(page).limit(limit).all()
            elif order_by and order_by.startswith('+'):
                # 升序
                order_name = order_by.split("+")[-1]
                if order_name in OrderNameEnum.__members__:
                    result_tuple = db.session.query(A, B).join(B, A.product_id == B.business_id).filter(
                        A.belong_to == dealer_name).order_by(asc(order_name)).offset(page).limit(limit).all()
                else:
                    result_tuple = db.session.query(A, B).join(B, A.product_id == B.business_id).filter(
                        A.belong_to == dealer_name).order_by(asc(A.update_time)).offset(page).limit(limit).all()
            else:
                result_tuple = db.session.query(A, B).join(B, A.product_id == B.business_id).filter(
                    A.belong_to == dealer_name).order_by(desc(A.update_time)).offset(page).limit(limit).all()

            return {
                "data": result_tuple,
                "count": DealerProductList.query.count()
            }


def get_product_by_business_id(business_id):
    """
    根据 业务id 获取产品详情信息
    :param business_id: 业务id
    :return:
    """
    return ProductList.query.filter_by(business_id=business_id).first()


def get_product_by_name_and_scent(product_name, scent_type, specifications):
    """
    根据 产品名称 和 香型 获取产品详情信息（产品名称、香型和规格可以唯一确定一个产品）
    :param product_name: 产品名称
    :param scent_type: 香型
    :param specifications: 产品规格
    :return:
    """
    return ProductList.query.filter_by(
        product_name=product_name, scent_type=scent_type, specifications=specifications
    ).first()


def dealer_product_is_exist(product_id, belong_to):
    """
    根据 产品id 判断经销商产品列表中是否存在该商品
    :param product_id: 产品id
    :param belong_to: 属于哪里的经销商
    :return:
    """
    return DealerProductList.query.filter_by(product_id=product_id, belong_to=belong_to).first()


def dealer_name_is_exist(dealer_name):
    """
    根据 经销商名称 判断经销商产品列表中是否存在该经销商
    :param dealer_name: 经销商名称
    :return:
    """
    return DealerList.query.filter_by(dealer_name=dealer_name).first()


def get_product_info_by_id(product_id):
    """
    根据 产品 business_id 获取产品详情信息
    :param product_id: 产品id
    :return:
    """
    return ProductList.query.filter_by(business_id=product_id).first()


def get_dealer_product_by_business_id(business_id):
    """
    根据 业务id 获取经销商产品详情信息
    :param business_id: 业务id
    :return:
    """
    return DealerProductList.query.filter_by(business_id=business_id).first()


def add_product(data: dict):
    """
    新增产品
    :param data: 数据字典
    :return:
    """
    try:
        db.session.add(ProductList(**data))
        db.session.commit()
        return ProductList.query.order_by(ProductList.create_time.desc()).first()
    except:
        db.session.rollback()
        raise AddProductException


def add_dealer_product(data: dict):
    """
    新增经销商产品
    :param data: 数据字典
    :return:
    """
    try:
        db.session.add(DealerProductList(**data))
        db.session.commit()
        return DealerProductList.query.order_by(DealerProductList.create_time.desc()).first()
    except:
        db.session.rollback()
        raise AddDealerProductException


def add_dealer_name(data: dict):
    """
    新增一个经销商名单
    :param data: 数据字典
    :return:
    """
    # 1. 将 parent_dealer 下的所有的产品拷贝一份给 当前的 dealer_name
    if data.get('parent_dealer'):
        result = get_all_dealer_product_list_by_dealer_name(dealer_name=data['parent_dealer'])
        data_list = result.get('data')
        for obj in data_list:
            params_dict = {
                "product_id": obj.product_id,
                "belong_to": data['dealer_name'],
                "unit_price": obj.unit_price,
                "price_of_piece": obj.price_of_piece,
                "wholesale_price": obj.wholesale_price,
                "suggested_retail_price": obj.suggested_retail_price,
                "scanning_price": obj.scanning_price,
                "remarks": obj.remarks,
            }
            try:
                add_dealer_product(params_dict)
            except:
                raise AddDealerProductException

    # 2. 将 dealer_name 写入数据库
    try:
        db.session.add(DealerList(**data))
        db.session.commit()
        return DealerList.query.order_by(DealerList.create_time.desc()).first()
    except:
        db.session.rollback()
        raise AddDealerNameException


def update_product_by_business_id(data_id: str, data):
    """
    根据业务id更新数据
    :param data_id:
    :param data:
    :return:
    """
    try:
        # 根据业务id查询这条数据
        product_obj = get_product_by_business_id(business_id=data_id)
        if product_obj:
            # 执行更新操作
            ProductList.query.filter(ProductList.business_id == data_id).update(data)
            db.session.commit()
    except:
        db.session.rollback()
        raise UpdateProductException


def update_dealer_product_by_business_id(data_id: str, data):
    """
    根据 业务id 更新将销售产品数据
    :param data_id:
    :param data:
    :return:
    """
    try:
        # 根据业务id查询这条数据
        product_obj = get_dealer_product_by_business_id(business_id=data_id)
        if product_obj:
            # 执行更新操作
            DealerProductList.query.filter(DealerProductList.business_id == data_id).update(data)
            db.session.commit()
    except:
        db.session.rollback()
        raise UpdateDealerProductException


def update_dealer_name_by_business_id(data_id: str, data):
    """
    根据 业务id 更新经销商列表 数据
    :param data_id: 业务id
    :param data: 数据dict
    :return:
    """
    try:
        # 根据业务id查询这条数据
        product_obj = get_dealer_list_by_id(data_id=data_id)
        if product_obj:
            # 执行更新操作
            DealerList.query.filter(DealerList.business_id == data_id).update(data)
            db.session.commit()
    except:
        db.session.rollback()
        raise UpdateDealerNameException


def delete_product_by_business_id(data_id: str):
    """
    根据 产品id 删除该条产品
    :param data_id: 产品id
    :return:
    """
    try:
        ProductList.query.filter(ProductList.business_id == data_id).delete()
        db.session.commit()
    except:
        db.session.rollback()
        raise DeleteProductException


def delete_dealer_product_by_business_id(data_id: str):
    """
    根据 产品id 删除该条经销商产品
    :param data_id: 产品id
    :return:
    """
    try:
        DealerProductList.query.filter(DealerProductList.business_id == data_id).delete()
        db.session.commit()
    except:
        db.session.rollback()
        raise DeleteDealerProductException


def delete_dealer_name_by_id(data_id: str, dealer_name: str):
    """
    根据 经销商名字id 删除该条经销商名字
    :param data_id: 业务id
    :param dealer_name: 经销商名字
    :return:
    """
    # 1. 删除该经销商名下所有的产品
    if dealer_name:
        try:
            DealerProductList.query.filter(DealerProductList.belong_to == dealer_name).delete()
            db.session.commit()
        except:
            db.session.rollback()
            raise DeleteDealerProductException

    # 2. 根据 业务id 删除这条 经销商名字数据
    try:
        DealerList.query.filter(DealerList.business_id == data_id).delete()
        db.session.commit()
    except:
        db.session.rollback()
        raise DeleteDealerNameException


def delete_multi_product_by_ids(data_ids: list):
    """
    根据 产品id数组 批量删除产品
    :param data_ids: 产品id
    :return:
    """
    try:
        ProductList.query.filter(ProductList.business_id.in_(data_ids)).delete()
        db.session.commit()
    except:
        db.session.rollback()
        raise MultiDeleteProductException


def delete_multi_dealer_product_by_ids(data_ids: list):
    """
    根据 产品id数组 批量删除经销商产品
    :param data_ids: 产品id
    :return:
    """
    try:
        DealerProductList.query.filter(DealerProductList.business_id.in_(data_ids)).delete()
        db.session.commit()
    except:
        db.session.rollback()
        raise MultiDeleteDealerProductException


def get_dealer_list_by_name(name: str):
    """
    获取经销商列表 by dealer_name
    :param name:
    :return:
    """
    return DealerList.query.filter_by(dealer_name=name).first()


def get_dealer_list_by_id(data_id: str):
    """
    获取经销商列表 by 业务id
    :param data_id: 业务id
    :return:
    """
    return DealerList.query.filter_by(business_id=data_id).first()

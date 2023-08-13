import uuid

from app_router.models.database import db


class StockList(db.Model):
    """
    股票操作表（动态路由）
    """
    __tablename__ = 'stock_list'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True,
                   nullable=False, comment="哈希自动生成id")
    stock_name = db.Column(db.String(255), nullable=False, comment="股票名称")
    stock_code = db.Column(db.String(255), nullable=False, comment="股票代码")
    # total_assets = db.Column(db.Float, comment="合计资产")
    remarks = db.Column(db.Text, nullable=True, comment="备注")

    # 公共字段
    is_delete = db.Column(db.Integer, default=0, nullable=False,
                          comment="逻辑删除，查询的时候按照 filter is_delete != 0 来过滤已经逻辑删除的数据")
    create_time = db.Column(
        db.TIMESTAMP, nullable=False, default=db.func.now(), server_default=db.func.now(),
        comment="创建时间，修改数据不会自动更改"
    )
    update_time = db.Column(
        db.TIMESTAMP, nullable=False, server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'),
        comment="更新时间"
    )
    business_id = db.Column(db.String(36), default=lambda: str(uuid.uuid4()), nullable=False, unique=True,
                            comment="业务id（使用雪花算法生成唯一id）")

    def __repr__(self):
        return '<AuthApi %r>' % self.title

    def as_dict(self):
        """
        输出为 dict
        :return:
        """
        _dict = {}
        for c in self.__table__.columns:
            if not isinstance(c.type, db.Enum):
                _dict[c.name] = getattr(self, c.name)
            else:
                _dict[c.name] = getattr(self, c.name).name
        return _dict


class TransactionList(db.Model):
    """
    交易列表
    """
    __tablename__ = 'transaction_list'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False,
                   comment="哈希自动生成id")
    stock_id = db.Column(db.String(255), nullable=False, comment="stock_list表的business_id")
    transaction_type = db.Column(db.String(255), nullable=False, comment="交易类型（买入或者卖出）")
    product_type = db.Column(db.String(255), nullable=False, comment="产品类型（股票或者基金）")
    buy_price = db.Column(db.Float, comment="买入价格")
    sell_price = db.Column(db.Float, comment="卖出价格")
    quantity = db.Column(db.Integer, nullable=False, comment="数量")
    subtotal_price = db.Column(db.Float, comment='小计价格')
    sell_gear_one = db.Column(db.Float, comment="卖出档位1（10%）")
    sell_gear_two = db.Column(db.Float, comment="卖出档位2（20%）")
    markup_price = db.Column(db.Float, comment="加仓价格")
    heavy_price = db.Column(db.Float, comment="重仓价格")
    remain_positions = db.Column(db.Float, comment="剩余仓位")
    profit_amount = db.Column(db.Float, comment='盈利数额')
    dividend_amount = db.Column(db.Integer, comment="分红金额")
    cost = db.Column(db.Float, comment='成本价格')
    transaction_status = db.Column(db.String(255), nullable=False, comment="交易状态", default="未清仓")
    remarks = db.Column(db.Text, comment="备注")

    # 公共字段
    is_delete = db.Column(db.Integer, default=0, nullable=False,
                          comment="逻辑删除，查询的时候按照 filter is_delete != 0 来过滤已经逻辑删除的数据")
    create_time = db.Column(
        db.TIMESTAMP, nullable=False, default=db.func.now(), server_default=db.func.now(),
        comment="创建时间，修改数据不会自动更改"
    )
    update_time = db.Column(
        db.TIMESTAMP, nullable=False, server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'),
        comment="更新时间"
    )
    business_id = db.Column(db.String(36), default=lambda: str(uuid.uuid4()), nullable=False, unique=True,
                            comment="业务id（使用雪花算法生成唯一id）")

    def __repr__(self):
        return '<TransactionList %r>' % self.product_name

    def as_dict(self):
        """
        输出为 dict
        :return:
        """
        _dict = {}
        for c in self.__table__.columns:
            if not isinstance(c.type, db.Enum):
                _dict[c.name] = getattr(self, c.name)
            else:
                _dict[c.name] = getattr(self, c.name).name
        return _dict

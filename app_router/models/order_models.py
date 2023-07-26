import uuid

from sqlalchemy.dialects.mysql import FLOAT

from app_router.models.database import db


class PurchaseOrder(db.Model):
    """
    入库单表
    """
    __tablename__ = 'purchase_order'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False,
                   comment="哈希自动生成id")
    title = db.Column(db.String(150), nullable=False, comment="入库单标题")
    total_price = db.Column(FLOAT(precision=10, scale=2), nullable=False, comment="本次入库总计（元）")
    total_piece = db.Column(FLOAT(precision=10, scale=2), nullable=False, comment="本次入库总计（件）")
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
        return '<PurchaseOrder %r>' % self.title

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


class PurchaseOrderList(db.Model):
    """
    入库货品单
    """
    __tablename__ = 'purchase_order_list'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False,
                   comment="哈希自动生成id")
    purchase_order_id = db.Column(
        db.String(150), nullable=False, comment="入库单表（purchase_order）的business id，与之关联"
    )
    product_id = db.Column(db.String(36), nullable=False, comment="所有产品表的业务id，与之关联产品的基础信息")
    quantity = db.Column(FLOAT(precision=10, scale=2), nullable=False, comment="数量（件）")
    subtotal_price = db.Column(FLOAT(precision=10, scale=2), nullable=False, comment="小计（元）")
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
        return '<PurchaseOrderList %r>' % self.product_name

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


class OutboundOrder(db.Model):
    """
    出库单表
    """
    __tablename__ = 'outbound_order'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False,
                   comment="哈希自动生成id")
    title = db.Column(db.String(150), nullable=False, comment="出库单标题，例如出库刘总经销商的货")
    belong_to = db.Column(db.String(10), nullable=False, comment="归属于哪里的经销商")
    phone = db.Column(db.String(11), comment="电话号码")
    address = db.Column(db.String(150), comment="地址")
    # 物流公司
    logistics_company = db.Column(db.String(150), comment='物流公司')
    # 单号
    logistics_num = db.Column(db.String(30), comment='物流单号')
    total_price = db.Column(FLOAT(precision=10, scale=2), nullable=False, comment="本次出库金额总计（元）")
    total_piece = db.Column(db.Integer, nullable=False, comment="本次出库数量总计（瓶）")
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
        return '<OutboundOrder %r>' % self.title

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


class OutboundOrderList(db.Model):
    """
    采购货品单
    """
    __tablename__ = 'outbound_order_list'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False,
                   comment="哈希自动生成id")
    outbound_order_id = db.Column(
        db.String(150), nullable=False, comment="出库单表（outbound_order）的business id，与之关联"
    )
    dealer_product_id = db.Column(db.String(36), nullable=False, comment="经销商产品表的业务id，与之关联产品的基础信息")
    quantity = db.Column(db.Integer, nullable=False, comment="数量（瓶）")
    subtotal_price = db.Column(FLOAT(precision=10, scale=2), nullable=False, comment="小计（元）")
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
        return '<OutboundOrderList %r>' % self.outbound_order_id

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

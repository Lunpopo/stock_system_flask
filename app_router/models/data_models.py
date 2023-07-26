import uuid

from sqlalchemy.dialects.mysql import FLOAT

from app_router.models.database import db
from enums.enums import ProductScentEnum


class ProductList(db.Model):
    """
    单品列表
    """
    __tablename__ = 'product_list'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False,
                   comment="哈希自动生成id")
    product_name = db.Column(db.String(100), nullable=False, comment="产品名称")
    specifications = db.Column(db.Integer, nullable=False, comment="规格（ML）")
    # 保存香型表的 business_id
    scent_type = db.Column(db.String(36), nullable=False, comment="香型")
    specification_of_piece = db.Column(db.Integer, nullable=False, comment="每件规格（瓶）")
    unit_price = db.Column(FLOAT(precision=11, scale=2), nullable=False, comment="单价（元/瓶）")
    price_of_piece = db.Column(FLOAT(precision=11, scale=2), nullable=False, comment="每件价格（元）")
    scanning_price = db.Column(FLOAT(precision=11, scale=2), nullable=False, comment="扫码价（元/瓶）")
    img_url = db.Column(db.String(300), comment="图片路径")
    thumb_img_url = db.Column(db.String(300), comment="缩略图路径")
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
        return '<ProductList %r>' % self.product_name

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


class DealerProductList(db.Model):
    """
    经销商价格表
    """
    __tablename__ = 'dealer_product_list'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False,
                   comment="哈希自动生成id")
    # 新增一列，关联自己的产品表的产品（以这个产品为蓝本，对于经销商的价格进行改造）
    product_id = db.Column(db.String(36), comment="关联自己的产品的 business_id", nullable=False)
    belong_to = db.Column(db.String(10), nullable=False, comment="归属于哪里的经销商")
    unit_price = db.Column(FLOAT(precision=11, scale=2), nullable=False, comment="出厂价（元/瓶）")
    price_of_piece = db.Column(FLOAT(precision=11, scale=2), nullable=False, comment="每件价格（元）")
    # 批发价
    wholesale_price = db.Column(FLOAT(precision=11, scale=2), nullable=False, comment="批发价（元）")
    suggested_retail_price = db.Column(FLOAT(precision=11, scale=2), nullable=False, comment="建议零售价（元/瓶）")
    scanning_price = db.Column(FLOAT(precision=11, scale=2), nullable=False, comment="扫码价（元/瓶）")
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
        return '<DealerProductList %r>' % self.product_id

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


class DealerList(db.Model):
    """
    经销商名单表
    """
    __tablename__ = 'dealer_list'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False,
                   comment="哈希自动生成id")
    dealer_name = db.Column(db.String(10), nullable=False, comment="归属于哪里的经销商，经销商名称")
    parent_dealer = db.Column(db.String(10), nullable=False, comment="拷贝哪个经销商的产品列表")
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
        return '<DealerList %r>' % self.dealer_name

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


class ScentType(db.Model):
    """
    白酒香型表
    """
    __tablename__ = 'scent_type'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False,
                   comment="哈希自动生成id")
    scent_type = db.Column(db.Enum(ProductScentEnum), nullable=False, comment="香型")

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
        return '<ScentType %r>' % self.scent_type

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

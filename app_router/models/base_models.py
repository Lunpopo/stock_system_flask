import uuid

from app_router.models.database import db


class AuthUser(db.Model):
    """
    用户表
    """
    __tablename__ = 'auth_user'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True,
                   nullable=False, comment="哈希自动生成id")
    username = db.Column(db.String(150), unique=True, index=True, comment="用户名", nullable=False)
    password = db.Column(db.String(128), comment="密码", nullable=False)
    register_ip = db.Column(db.String(16), comment="注册ip")
    status = db.Column(db.Integer, default=0, comment="状态，是否可用")
    group_id = db.Column(db.String(36), nullable=False, comment="auth_group表的id，外键id")

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
        return '<User %r>' % self.username


class AuthGroup(db.Model):
    """
    用户组
    """
    __tablename__ = 'auth_group'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True,
                   nullable=False, comment="哈希自动生成id")
    group_name = db.Column(db.String(150), unique=True, comment="用户名key，例如editor", nullable=False)
    group_label = db.Column(
        db.String(150), nullable=False, comment="组名，普通用户组（默认）；用户管理组；数据管理组；超级管理员组"
    )
    description = db.Column(db.Text, comment="描述信息")

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
        return '<AuthGroup %r>' % self.group_name

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


class AuthFunction(db.Model):
    """
    api权限表（功能权限表）
    """
    __tablename__ = 'auth_function'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True,
                   nullable=False, comment="哈希自动生成id")
    api_name = db.Column(
        db.String(150), unique=True, index=True, comment="api的路径，例如：/user/get_group_data", nullable=False
    )
    title = db.Column(db.String(150), comment="api的title名字，例如：货单表格")
    description = db.Column(db.Text, comment="api的描述信息")
    permission = db.Column(
        db.String(50), comment="此api的权限，用:隔开，例如：admin:editor 就是只允许admin和editor的权限",
        default="0", nullable=False
    )

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
        return '<AuthFunction %r>' % self.title

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


class AuthApi(db.Model):
    """
    菜单权限表（动态路由）
    """
    __tablename__ = 'auth_api'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True,
                   nullable=False, comment="哈希自动生成id")
    api_parent_id = db.Column(db.String(36), comment="菜单的父级-树形结构")
    vue_name = db.Column(db.String(150), comment="Vue中展示的名字")
    title = db.Column(db.String(150), comment="api的title名字，例如：货单表格")
    description = db.Column(db.Text, comment="api的描述信息")
    icon = db.Column(db.String(50), comment="api的icon字段，例如：table")
    menu_type = db.Column(db.Integer, comment="菜单的等级，一级菜单为0，二级菜单为1，后面的类推", nullable=False)
    hidden = db.Column(db.Integer, comment="是否隐藏，0为不隐藏，1为隐藏", default=0)
    permission = db.Column(
        db.String(50), comment="此api的权限，用:隔开，例如：admin:editor 就是只允许admin和editor的权限",
        default="0", nullable=False
    )
    redirect = db.Column(db.String(150), comment="一级目录的中定向到的页面")

    router_path = db.Column(
        db.String(150), comment="路由路径，例如：/user/get_group_data，子路由就与父路由的路径进行拼接", nullable=False
    )
    component_path = db.Column(db.String(150), comment="组件路径，例如：views/product/myself-price-list", nullable=False)

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
    cost = db.Column(db.Float, comment='成本价格')
    transaction_status = db.Column(db.String(255), comment="交易状态")
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

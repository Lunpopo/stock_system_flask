# 创建数据模型
import typing

from pydantic import BaseModel


class UpdateUserSettingVO(BaseModel):
    """
    更新用户设置页面的入参参数
    """
    username: typing.AnyStr
    phone: typing.AnyStr
    email: typing.AnyStr


class DeleteByIdDFromUserVO(BaseModel):
    """
    通过 表id 删除 data_ship 表数据的入参参数
    """
    data: typing.Any


class DeleteByIdDFromAirplaneVO(BaseModel):
    """
    通过 表id 删除 data_airplane 数据的入参参数
    """
    data: typing.Any


class UpdateAirplaneVO(BaseModel):
    """
    通过 表id 更新 data_airplane 数据的入参参数
    """
    data: typing.Any


class UpdatePermissionVO(BaseModel):
    """
    更新 权限 入参参数
    """
    data: typing.Any


class AddAirplaneVO(BaseModel):
    primary_user: str
    attending_time: str
    model: str
    first_flight: str
    role: str
    retire: str
    producer: str
    maker: str
    variants: str
    status: str
    product_year: str
    category: str
    engine_num: str
    height: str
    wingspan: str
    aerodynamic_configuration: str
    speed: str
    crew: str
    length: str
    gross_weight: str
    engine: str
    max_takeoff_weight: str
    max_fly_speed: str
    range: str
    airplane_yield: str
    service_ceiling: str
    wing_area: str
    load_weight: str
    normal_takeoff_weight: str
    thrust: str
    cruising_speed: str
    combat_radius: str
    wing_loading: str
    max_overload: str
    takeoff_distance: str
    weapon: str
    thrust_weight_ratio: str
    unit_costs: str


class AddHistoryVO(BaseModel):
    """
    通过 表id 更新 data_history 表数据的入参参数
    """
    backdrop: str
    process: str
    result: str
    combatants: str
    commander: str
    troop: str
    lose: str
    influence: str
    participants: str
    date: str
    location: str


class DeleteByIdDFromHistoryVO(BaseModel):
    """
    通过 表id 删除 data_history 表数据的入参参数
    """
    data: typing.Any


class UpdateHistoryVO(BaseModel):
    """
    通过 表id 更新 data_history 表数据的入参参数
    """
    data: typing.Any


class DeleteByIdDFromShipVO(BaseModel):
    """
    通过 表id 删除 data_ship 表数据的入参参数
    """
    data: typing.Any


class UpdateShipVO(BaseModel):
    """
    通过 表id 更新 data_ship 表数据的入参参数
    """
    data: typing.Any


class DeleteByIdDFromWeaponVO(BaseModel):
    """
    通过 表id 删除 data_weapon 表数据的入参参数
    """
    data: typing.Any


class UpdateWeaponVO(BaseModel):
    """
    通过 表id 更新 data_weapon 表数据的入参参数
    """
    data: typing.Any


class UpdateBaseVO(BaseModel):
    """
    通过 表id 更新 data_base 表数据的入参参数
    """
    data: typing.Any


class UpdateUserVO(BaseModel):
    """
    通过 表id 更新 data_user 表数据的入参参数
    """
    data: typing.Any


class BaseData(BaseModel):
    title: str
    type: str
    category: str
    source: str
    url: str
    img: str
    abs: str

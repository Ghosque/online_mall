import xadmin
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget

from .models import Buyer, Province, City, Area, Address
from adminx import *


@xadmin.sites.register(Buyer)
class BuyerAdmin:
    list_display = ('id', 'open_id', 'nickname', 'gender', 'avatar', 'language', 'area', 'reward_points', 'create_time', 'update_time',)
    list_filter = ('gender', 'language', 'area',)
    search_fields = ('open_id', 'nickname',)
    ordering = ('id',)
    readonly_fields = ('create_time', 'update_time',)


class ProvinceResource(resources.ModelResource):

    class Meta:
        model = Province


@xadmin.sites.register(Province)
class ProvinceAdmin:
    import_export_args = {'import_resource_class': ProvinceResource}

    list_display = ('id', 'province_id', 'province', 'create_time', 'update_time',)
    list_filter = ('province',)
    search_fields = ('province',)
    ordering = ('id',)
    readonly_fields = ('create_time', 'update_time',)


class CityResource(resources.ModelResource):
    province = fields.Field(
        column_name='province',
        attribute='province',
        widget=ForeignKeyWidget(Province, 'province_id'))

    class Meta:
        model = City
        fields = ('id', 'city_id', 'city', 'province',)


@xadmin.sites.register(City)
class CityAdmin:
    import_export_args = {'import_resource_class': CityResource}

    list_display = ('id', 'city_id', 'city', 'province', 'create_time', 'update_time',)
    list_filter = ('province',)
    search_fields = ('city',)
    ordering = ('id',)
    readonly_fields = ('create_time', 'update_time',)


class AreaResource(resources.ModelResource):
    city = fields.Field(
        column_name='city',
        attribute='city',
        widget=ForeignKeyWidget(City, 'city_id'))

    class Meta:
        model = Area
        fields = ('id', 'area_id', 'area', 'city',)


@xadmin.sites.register(Area)
class AreaAdmin:
    import_export_args = {'import_resource_class': AreaResource}

    list_display = ('id', 'area_id', 'area', 'city', 'create_time', 'update_time',)
    list_filter = ('city',)
    search_fields = ('area',)
    ordering = ('id',)
    readonly_fields = ('create_time', 'update_time',)


@xadmin.sites.register(Address)
class AddressAdmin:
    list_display = ('id', 'detail_address', 'contact', 'addressee', 'is_default', 'province', 'city', 'area', 'buyer', 'create_time', 'update_time',)
    list_filter = ('province', 'city', 'area', 'buyer', 'is_default',)
    search_fields = ('buyer',)
    ordering = ('id',)
    readonly_fields = ('create_time', 'update_time',)

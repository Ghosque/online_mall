import xadmin
from xadmin import views
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget

from .models import User, FollowCommodity, ShoppingCart, Province, City, Area, Address


@xadmin.sites.register(User)
class UserAdmin:
    list_display = ('id', 'user_id', 'nickname', 'password', 'phone', 'reward_points', 'create_time', 'update_time')
    list_filter = ('id',)
    search_fields = ('user_id',)
    ordering = ('id',)
    readonly_fields = ('create_time', 'update_time',)

    model_icon = 'fa fa-user'


@xadmin.sites.register(FollowCommodity)
class FollowCommodityAdmin:
    list_display = ('id', 'status', 'user', 'commodity', 'create_time', 'update_time')
    list_filter = ('id', 'status',)
    search_fields = ('user', 'commodity',)
    ordering = ('id',)
    readonly_fields = ('create_time', 'update_time',)


@xadmin.sites.register(ShoppingCart)
class ShoppingCartAdmin:
    list_display = ('id', 'quantity', 'user', 'commodity', 'create_time', 'update_time')
    list_filter = ('id',)
    search_fields = ('user', 'commodity',)
    ordering = ('id',)
    readonly_fields = ('create_time', 'update_time',)


class ProvinceResource(resources.ModelResource):

    class Meta:
        model = Province
        fields = ('id', 'province_id', 'province',)


@xadmin.sites.register(Province)
class ProvinceCartAdmin:
    import_export_args = {'import_resource_class': ProvinceResource}

    list_display = ('id', 'province_id', 'province', 'create_time', 'update_time')
    list_filter = ('id',)
    search_fields = ('province',)
    ordering = ('province_id',)
    readonly_fields = ('create_time', 'update_time',)


class CityResource(resources.ModelResource):
    province_id = fields.Field(
        column_name='province',
        attribute='province',
        widget=ForeignKeyWidget(Province, 'province_id'))

    class Meta:
        model = City
        fields = ('id', 'city_id', 'city', 'province_id',)


@xadmin.sites.register(City)
class CityCartAdmin:
    import_export_args = {'import_resource_class': CityResource}

    list_display = ('id', 'city_id', 'city', 'province', 'create_time', 'update_time')
    list_filter = ('id',)
    search_fields = ('city',)
    ordering = ('city_id',)
    readonly_fields = ('create_time', 'update_time',)


class AreaResource(resources.ModelResource):
    city_id = fields.Field(
        column_name='city',
        attribute='city',
        widget=ForeignKeyWidget(City, 'city_id'))

    class Meta:
        model = Area
        fields = ('id', 'area_id', 'area', 'city_id',)


@xadmin.sites.register(Area)
class AreaCartAdmin:
    import_export_args = {'import_resource_class': AreaResource}
    list_display = ('id', 'area_id', 'area', 'city', 'create_time', 'update_time')
    list_filter = ('id',)
    search_fields = ('area',)
    ordering = ('area_id',)
    readonly_fields = ('create_time', 'update_time',)


@xadmin.sites.register(Address)
class AddressCartAdmin:
    list_display = ('id', 'detail_address', 'contact', 'addressee', 'is_default', 'province', 'city', 'area', 'user', 'create_time', 'update_time')
    list_filter = ('id', 'user', 'is_default',)
    search_fields = ('user',)
    ordering = ('id',)
    readonly_fields = ('create_time', 'update_time',)

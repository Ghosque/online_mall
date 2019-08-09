import xadmin
from xadmin import views

from .models import FirstCategory, SecondCategory, Merchant, Shop, Commodity, CommodityColor, Specification


@xadmin.sites.register(views.CommAdminView)
class GlobalSettings(object):
    site_title = 'online mall后台'
    site_footer = '2019 Ghosque, Inc. All rights reserved.'
    # menu_style = 'accordion'


@xadmin.sites.register(views.BaseAdminView)
class BaseSetting:
    enable_themes = True
    use_bootswatch = True


@xadmin.sites.register(FirstCategory)
class FirstCategoryAdmin:
    list_display = ('id', 'name', 'status', 'create_time', 'update_time')
    list_filter = ('id', 'status',)
    search_fields = ('name',)
    ordering = ('id',)
    readonly_fields = ('create_time', 'update_time',)


@xadmin.sites.register(SecondCategory)
class SecondCategoryAdmin:
    list_display = ('id', 'name', 'status', 'first_category', 'create_time', 'update_time')
    list_filter = ('id', 'status',)
    search_fields = ('name',)
    ordering = ('id',)
    readonly_fields = ('create_time', 'update_time',)


@xadmin.sites.register(Merchant)
class MerchantAdmin:
    list_display = ('id', 'merchant_id', 'password', 'name', 'gender', 'age', 'phone', 'id_card', 'create_time', 'update_time',)
    list_filter = ('id',)
    search_fields = ('merchant_id',)
    ordering = ('id',)
    readonly_fields = ('create_time', 'update_time',)

    model_icon = 'fa fa-user'


@xadmin.sites.register(Shop)
class ShopAdmin:
    list_display = ('id', 'shop_id', 'name', 'star', 'status', 'merchant', 'create_time', 'update_time',)
    list_filter = ('id', 'status',)
    search_fields = ('title', 'shop_id', 'name',)
    ordering = ('id',)
    readonly_fields = ('create_time', 'update_time',)


@xadmin.sites.register(Commodity)
class CommodityAdmin:
    list_display = ('id', 'commodity_id', 'title', 'title_desc', 'url', 'cover', 'status', 'inventory', 'category', 'shop', 'create_time', 'update_time',)
    list_filter = ('id', 'status', 'category',)
    search_fields = ('title', 'category',)
    ordering = ('id',)
    readonly_fields = ('create_time', 'update_time',)


@xadmin.sites.register(CommodityColor)
class CommodityColorAdmin:
    list_display = ('id', 'commodity_class', 'size', 'commodity', 'create_time', 'update_time',)
    list_filter = ('id',)
    search_fields = ('id', 'commodity',)
    ordering = ('id',)
    readonly_fields = ('create_time', 'update_time',)


@xadmin.sites.register(Specification)
class Specification:
    list_display = ('id', 'infomation', 'commodity', 'create_time', 'update_time',)
    list_filter = ('id',)
    search_fields = ('id', 'commodity',)
    ordering = ('id',)
    readonly_fields = ('create_time', 'update_time',)

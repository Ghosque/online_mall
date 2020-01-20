import xadmin

from .models import FirstCategory, SecondCategory, Merchant, Shop, Commodity, CommodityColor, Specification,\
    BackStageFirst, BackStageSecond, ThirdCategory, MerchantImage
from adminx import *


@xadmin.sites.register(Merchant)
class MerchantAdmin:
    list_display = ('id', 'merchant_id', 'name', 'gender', 'phone', 'user', 'create_time', 'update_time',)
    search_fields = ('user',)
    ordering = ('id',)
    readonly_fields = ('create_time', 'update_time',)


@xadmin.sites.register(MerchantImage)
class MerchantImageAdmin:
    list_display = ('id', 'name', 'oss_object', 'img', 'status', 'merchant', 'create_time', 'update_time',)
    search_fields = ('merchant',)
    ordering = ('id',)
    readonly_fields = ('create_time', 'update_time',)


@xadmin.sites.register(Shop)
class ShopAdmin:
    list_display = ('id', 'shop_id', 'name', 'star', 'status', 'create_time', 'update_time',)
    list_filter = ('status',)
    search_fields = ('name',)
    ordering = ('id',)
    readonly_fields = ('create_time', 'update_time',)


@xadmin.sites.register(Commodity)
class CommodityAdmin:
    list_display = ('id', 'commodity_id', 'name', 'title', 'title_desc', 'cover', 'display_images', 'status', 'inventory', 'price', 'category', 'shop', 'create_time', 'update_time',)
    list_filter = ('status',)
    search_fields = ('name', 'category', 'shop',)
    ordering = ('id',)
    readonly_fields = ('create_time', 'update_time',)


@xadmin.sites.register(CommodityColor)
class CommodityColorAdmin:
    list_display = ('id', 'commodity_class', 'commodity', 'create_time', 'update_time',)
    list_filter = ('commodity',)
    search_fields = ('commodity',)
    ordering = ('id',)
    readonly_fields = ('create_time', 'update_time',)


@xadmin.sites.register(Specification)
class SpecificationAdmin:
    list_display = ('id', 'information', 'commodity', 'create_time', 'update_time',)
    list_filter = ('commodity',)
    search_fields = ('commodity',)
    ordering = ('id',)
    readonly_fields = ('create_time', 'update_time',)


@xadmin.sites.register(FirstCategory)
class FirstCategoryAdmin:
    list_display = ('id', 'name', 'status', 'create_time', 'update_time',)
    list_filter = ('status',)
    search_fields = ('name',)
    ordering = ('id',)
    readonly_fields = ('create_time', 'update_time',)


@xadmin.sites.register(SecondCategory)
class SecondCategoryAdmin:
    list_display = ('id', 'name', 'status', 'first_category', 'create_time', 'update_time',)
    list_filter = ('first_category', 'status',)
    search_fields = ('name',)
    ordering = ('id',)
    readonly_fields = ('create_time', 'update_time',)


@xadmin.sites.register(ThirdCategory)
class ThirdCategoryAdmin:
    list_display = ('id', 'name', 'image', 'status', 'second_category', 'create_time', 'update_time',)
    list_filter = ('second_category', 'status',)
    search_fields = ('name',)
    ordering = ('id',)
    readonly_fields = ('create_time', 'update_time',)


@xadmin.sites.register(BackStageFirst)
class BackStageFirstAdmin:
    list_display = ('id', 'name', 'status', 'create_time', 'update_time',)
    list_filter = ('status',)
    search_fields = ('name',)
    ordering = ('id',)
    readonly_fields = ('create_time', 'update_time',)


@xadmin.sites.register(BackStageSecond)
class BackStageSecondAdmin:
    list_display = ('id', 'name', 'status', 'first', 'create_time', 'update_time',)
    list_filter = ('first', 'status',)
    search_fields = ('name',)
    ordering = ('id',)
    readonly_fields = ('create_time', 'update_time',)

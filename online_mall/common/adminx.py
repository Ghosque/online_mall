import xadmin

from .models import DisplayImage, FirstColorSelector, SecondColorSelector, Commodity, CommodityColor, Specification,\
    CardTicket, CommodityComment


@xadmin.sites.register(DisplayImage)
class DisplayImageAdmin:
    list_display = ('id', 'image', 'is_display', 'create_time', 'update_time',)
    list_filter = ('is_display',)
    search_fields = ('image',)
    ordering = ('id',)
    readonly_fields = ('create_time', 'update_time',)


@xadmin.sites.register(FirstColorSelector)
class FirstColorSelectorAdmin:
    list_display = ('id', 'name', 'color_code', 'status', 'create_time', 'update_time',)
    list_filter = ('status',)
    search_fields = ('name',)
    ordering = ('id',)
    readonly_fields = ('create_time', 'update_time',)


@xadmin.sites.register(SecondColorSelector)
class SecondColorSelectorAdmin:
    list_display = ('id', 'name', 'color_code', 'status', 'first', 'create_time', 'update_time',)
    list_filter = ('status', 'first',)
    search_fields = ('name', 'first',)
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


@xadmin.sites.register(CardTicket)
class ReduceCardTicketAdmin:
    list_display = ('id', 'type', 'quota', 'min_price_limit', 'deadline', 'commodity_limit', 'category_limit', 'buyer', 'create_time', 'update_time',)
    list_filter = ('buyer', 'commodity_limit', 'category_limit',)
    search_fields = ('buyer', 'commodity_limit', 'category_limit',)
    ordering = ('id',)
    readonly_fields = ('create_time', 'update_time',)


@xadmin.sites.register(CommodityComment)
class CommodityCommentAdmin:
    list_display = ('id', 'content', 'score', 'commodity', 'commentator', 'create_time', 'update_time',)
    list_fliter = ('score', 'commodity', 'commentator',)
    search_fields = ('commodity', 'commentator',)
    ordering = ('id',)
    readonly_fields = ('create_time', 'update_time',)

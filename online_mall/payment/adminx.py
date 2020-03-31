import xadmin

from .models import Order, SinglePurchaseOrder, CommodityComment, SecondComment, CommentPaise


@xadmin.sites.register(Order)
class OrderAdmin:
    list_display = ('id', 'order_id', 'info', 'status', 'buyer', 'address', 'create_time', 'update_time',)
    list_filter = ('status', 'buyer',)
    search_fields = ('order_id', 'buyer',)
    ordering = ('id',)
    readonly_fields = ('create_time', 'update_time',)


@xadmin.sites.register(SinglePurchaseOrder)
class SinglePurchaseOrderAdmin:
    list_display = ('id', 'purchase_id', 'status', 'item_index', 'num', 'commodity', 'order', 'create_time', 'update_time',)
    list_filter = ('status', 'commodity', 'order',)
    search_fields = ('purchase_id', 'commodity', 'order',)
    ordering = ('id',)
    readonly_fields = ('create_time', 'update_time',)


@xadmin.sites.register(CommodityComment)
class CommodityCommentAdmin:
    list_display = ('id', 'content', 'commodity_star', 'shop_star', 'logistics_star', 'status', 'buyer', 'single_purchase_order', 'create_time', 'update_time',)
    list_filter = ('status', 'buyer', 'single_purchase_order',)
    search_fields = ('content', 'buyer', 'single_purchase_order',)
    ordering = ('id',)
    readonly_fields = ('create_time', 'update_time',)


@xadmin.sites.register(SecondComment)
class SecondCommentAdmin:
    list_display = ('id', 'content', 'status', 'parent', 'create_time', 'update_time',)
    list_filter = ('status', 'parent',)
    search_fields = ('content', 'parent',)
    ordering = ('id',)
    readonly_fields = ('create_time', 'update_time',)


@xadmin.sites.register(CommentPaise)
class CommentPaiseAdmin:
    list_display = ('id', 'status', 'buyer', 'first_comment', 'second_comment', 'create_time', 'update_time',)
    list_filter = ('status', 'buyer', 'first_comment', 'second_comment',)
    search_fields = ('content', 'buyer', 'first_comment', 'second_comment',)
    ordering = ('id',)
    readonly_fields = ('create_time', 'update_time',)

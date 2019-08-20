import xadmin

from .models import Order


@xadmin.sites.register(Order)
class OrderAdmin:
    list_display = ('id', 'order_id', 'info', 'status', 'buyer', 'address', 'create_time', 'update_time',)
    list_filter = ('status', 'buyer',)
    search_fields = ('order_id', 'buyer',)
    ordering = ('id',)
    readonly_fields = ('create_time', 'update_time',)

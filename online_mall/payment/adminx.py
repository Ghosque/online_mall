import xadmin
from xadmin import views

from .models import Order


@xadmin.sites.register(Order)
class OrderAdmin:
    list_display = ('id', 'order_id', 'info', 'status', 'user', 'address', 'create_time', 'update_time')
    list_filter = ('id', 'status',)
    search_fields = ('order_id',)
    ordering = ('id',)
    readonly_fields = ('create_time', 'update_time',)

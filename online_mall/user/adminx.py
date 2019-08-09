import xadmin
from xadmin import views

from .models import User, FollowCommodity, ShoppingCart, Address


@xadmin.sites.register(User)
class UserAdmin:
    list_display = ('id', 'user_id', 'nickname', 'password', 'phone', 'reward_points', 'create_time', 'update_time')
    list_filter = ('id',)
    search_fields = ('user_id',)
    ordering = ('id',)
    readonly_fields = ('create_time', 'update_time',)


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


@xadmin.sites.register(Address)
class AddressCartAdmin:
    list_display = ('id', 'address', 'contact', 'addressee', 'is_default', 'user', 'create_time', 'update_time')
    list_filter = ('id', 'user', 'is_default',)
    search_fields = ('user',)
    ordering = ('id',)
    readonly_fields = ('create_time', 'update_time',)

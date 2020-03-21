import xadmin
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget

from .models import Buyer, Address
from adminx import *


@xadmin.sites.register(Buyer)
class BuyerAdmin:
    list_display = ('id', 'open_id', 'nickname', 'gender', 'avatar', 'language', 'area', 'reward_points', 'create_time', 'update_time',)
    list_filter = ('gender', 'language', 'area',)
    search_fields = ('open_id', 'nickname',)
    ordering = ('id',)
    readonly_fields = ('create_time', 'update_time',)


@xadmin.sites.register(Address)
class AddressAdmin:
    list_display = ('id', 'detail_address', 'contact', 'addressee', 'is_default', 'buyer', 'create_time', 'update_time',)
    list_filter = ('buyer', 'is_default',)
    search_fields = ('buyer',)
    ordering = ('id',)
    readonly_fields = ('create_time', 'update_time',)

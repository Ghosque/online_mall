import xadmin

from .models import MallUser, VerifyCode


@xadmin.sites.register(MallUser)
class MallUserAdmin:
    list_display = ('id', 'name', 'gender', 'phone', 'id_card', 'is_merchant', 'user', 'create_time', 'update_time',)
    list_filter = ('gender', 'is_merchant',)
    search_fields = ('name', 'user',)
    ordering = ('id',)
    readonly_fields = ('create_time', 'update_time',)


@xadmin.sites.register(VerifyCode)
class VerifyCodeAdmin:
    list_display = ('id', 'code', 'phone', 'create_time', 'update_time',)
    list_filter = ('phone',)
    search_fields = ('phone',)
    ordering = ('id',)
    readonly_fields = ('create_time', 'update_time',)

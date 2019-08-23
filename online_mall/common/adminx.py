import xadmin

from .models import MallUser, DisplayImage, CommentLabel


@xadmin.sites.register(MallUser)
class MallUserAdmin:
    list_display = ('id', 'name', 'gender', 'phone', 'id_card', 'is_merchant', 'user', 'create_time', 'update_time',)
    list_filter = ('gender', 'is_merchant',)
    search_fields = ('name', 'user',)
    ordering = ('id',)
    readonly_fields = ('create_time', 'update_time',)


@xadmin.sites.register(DisplayImage)
class DisplayImageAdmin:
    list_display = ('id', 'image', 'is_display', 'create_time', 'update_time',)
    list_filter = ('is_display',)
    search_fields = ('image',)
    ordering = ('id',)
    readonly_fields = ('create_time', 'update_time',)


@xadmin.sites.register(CommentLabel)
class CommentLabelAdmin:
    list_display = ('id', 'label', 'is_delete', 'create_time', 'update_time',)
    list_filter = ('is_delete',)
    search_fields = ('label',)
    ordering = ('id',)
    readonly_fields = ('create_time', 'update_time',)

import xadmin

from .models import DisplayImage, CommentLabel, FirstColorSelector, SecondColorSelector


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

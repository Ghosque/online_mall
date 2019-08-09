from django.db import models

from merchant.models import Commodity
from common import GetId


# 用户
class User(models.Model):
    user_id = models.CharField(default=GetId.getId(), max_length=15, verbose_name='用户ID')
    nickname = models.CharField(max_length=30, verbose_name='昵称')
    password = models.CharField(max_length=50, verbose_name='密码')
    phone = models.CharField(max_length=15, verbose_name='手机号码')
    reward_points = models.IntegerField(default=0, verbose_name='积分')

    create_time = models.DateTimeField(auto_now_add=True, editable=False, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, editable=False, verbose_name='修改时间')

    class Meta:
        verbose_name = verbose_name_plural = '用户'
        unique_together = ('user_id', 'phone',)

    def __str__(self):
        return self.nickname


# 用户关注商品
class FollowCommodity(models.Model):
    STATUS_ITEMS = (
        (1, '正常'),
        (0, '删除'),
    )

    status = models.SmallIntegerField(choices=STATUS_ITEMS, verbose_name='状态')

    create_time = models.DateTimeField(auto_now_add=True, editable=False, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, editable=False, verbose_name='修改时间')

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    commodity = models.ForeignKey(Commodity, on_delete=models.DO_NOTHING, verbose_name='商品')

    class Meta:
        verbose_name = verbose_name_plural = '商品关注'


# 购物车
class ShoppingCart(models.Model):
    quantity = models.IntegerField(verbose_name='数量')

    create_time = models.DateTimeField(auto_now_add=True, editable=False, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, editable=False, verbose_name='修改时间')

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    commodity = models.ForeignKey(Commodity, on_delete=models.DO_NOTHING, verbose_name='商品')

    class Meta:
        verbose_name = verbose_name_plural = '购物车'


class Address(models.Model):
    address = models.CharField(max_length=300, verbose_name='地址')
    contact = models.CharField(max_length=15, verbose_name='联系方式')
    addressee = models.CharField(max_length=15, verbose_name='收件人')
    is_default = models.BooleanField(verbose_name='是否为默认地址')

    create_time = models.DateTimeField(auto_now_add=True, editable=False, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, editable=False, verbose_name='修改时间')

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')

    class Meta:
        verbose_name = verbose_name_plural = '地址'

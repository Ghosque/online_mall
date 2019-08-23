from django.db import models
from django_mysql.models import JSONField

from buyer.models import Buyer, Address
from merchant.models import Commodity
from common_function.get_id import GetId


# 购物车
class ShoppingCart(models.Model):
    quantity = models.IntegerField(verbose_name='数量')

    create_time = models.DateTimeField(auto_now_add=True, editable=False, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, editable=False, verbose_name='修改时间')

    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE, verbose_name='买家')
    commodity = models.ForeignKey(Commodity, on_delete=models.DO_NOTHING, verbose_name='商品')

    class Meta:
        verbose_name = verbose_name_plural = '购物车'


# 订单
class Order(models.Model):
    STATUS_ITEMS = (
        (0, '删除'),
        (1, '待支付'),
        (2, '已支付'),
    )

    order_id = models.CharField(default=GetId.getId(), max_length=15, verbose_name='订单ID')
    info = JSONField(verbose_name='订单内容')
    price = models.IntegerField(verbose_name='总价格')
    status = models.SmallIntegerField(default=1, choices=STATUS_ITEMS, verbose_name='状态')

    create_time = models.DateTimeField(auto_now_add=True, editable=False, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, editable=False, verbose_name='修改时间')

    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE, verbose_name='买家')
    address = models.ForeignKey(Address, on_delete=models.CASCADE, verbose_name='地址')

    class Meta:
        verbose_name = verbose_name_plural = '订单'

    def __str__(self):
        return self.order_id


# 单件商品订单
class SinglePurchaseOrder(models.Model):
    STATUS_ITEMS = (
        (0, '删除'),
        (1, '待支付'),
        (2, '已支付'),
        (3, '正在出库'),
        (4, '已出库'),
        (5, '派送中'),
        (6, '确认收货'),
        (7, '待评价'),
        (8, '已完成'),
    )

    purchase_id = models.CharField(default=GetId.getOrderId(), max_length=18, verbose_name='单件商品订单号')

    create_time = models.DateTimeField(auto_now_add=True, editable=False, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, editable=False, verbose_name='修改时间')

    commodity = models.ForeignKey(Commodity, on_delete=models.DO_NOTHING, verbose_name='商品')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name='订单')

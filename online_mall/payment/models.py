from django.db import models
from django_mysql.models import JSONField, ListTextField

from buyer.models import Buyer, Address
from common.models import Commodity
from common_function.get_id import GetId
from common_function.get_timestamp import get_now_timestamp


# 订单
class Order(models.Model):
    STATUS_ITEMS = (
        (0, '已取消'),
        (1, '待支付'),
        (2, '已支付'),
    )

    order_id = models.CharField(default=GetId.getOrderId(), max_length=15, verbose_name='订单ID')
    info = JSONField(verbose_name='订单内容')
    status = models.SmallIntegerField(default=1, choices=STATUS_ITEMS, verbose_name='状态')
    price = models.IntegerField(verbose_name='总价格')
    expiration = models.CharField(max_length=20, verbose_name='过期时间')

    create_time = models.DateTimeField(auto_now_add=True, editable=False, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, editable=False, verbose_name='修改时间')

    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE, verbose_name='买家')
    address = models.ForeignKey(Address, on_delete=models.CASCADE, verbose_name='地址')

    class Meta:
        verbose_name = verbose_name_plural = '订单'
        ordering = ('-create_time',)

    def __str__(self):
        return self.order_id

    @classmethod
    def save_data(cls, data_dict, buyer):
        # 商品id item_index num
        address = Address.objects.get(pk=data_dict['address'])
        order_id = GetId.getOrderId()
        while cls.objects.filter(order_id=order_id):
            order_id = GetId.getOrderId()

        order = cls.objects.create(
            order_id=order_id,
            info=data_dict['info'],
            price=data_dict['price'],
            status=1,
            expiration=data_dict['expiration'],
            buyer=buyer,
            address=address
        )

        return order

    @classmethod
    def handle_unpaid_data(cls, now_timestamp):
        data_list = cls.objects.filter(status=1)
        for item in data_list:
            if now_timestamp > float(item.expiration):
                item.status = 0
                item.save()

    @classmethod
    def get_canceled_data(cls, buyer, status):
        data_list = list()
        data = cls.objects.filter(status__in=[0, 1], buyer=buyer)
        for item in data:
            if item.status == status:
                data_list.append(cls.serialize_data(item))
            else:
                now_timestamp = get_now_timestamp()
                if float(item.expiration) <= now_timestamp:
                    data_list.append(cls.serialize_data(item, status))

        return data_list

    @classmethod
    def get_to_be_paid_data(cls, buyer, status):
        data_list = list()
        data = cls.objects.filter(status=1, buyer=buyer)
        for item in data:
            now_timestamp = get_now_timestamp()
            if float(item.expiration) > now_timestamp:
                data_list.append(cls.serialize_data(item, status))

        return data_list

    @classmethod
    def get_paid_data(cls, buyer):
        data_list = list()
        data = cls.objects.filter(status=2, buyer=buyer)
        for item in data:
            data_list.append(item)

        return data_list

    @classmethod
    def get_single_data(cls, order_id, status):
        data = cls.serialize_data(cls.objects.get(order_id=order_id), status)

        return data

    @staticmethod
    def serialize_data(data, status, has_address=False):
        if not has_address:
            address = ''.join(eval(data.address.region)) + data.address.detail
        else:
            address = data.address.address

        data_dict = {
            'id': data.id,
            'order_id': data.order_id,
            'status': status,
            'info': data.info,
            'price': data.price,
            'expiration': data.expiration,
            'address': {
                'id': data.address.id,
                'name': data.address.name,
                'address': address,
                'phone': data.address.phone,
            },
            'create_time': data.create_time,
            'update_time': data.update_time,
            'is_single': False
        }

        return data_dict

    @classmethod
    def complete_order(cls, order_id):
        order = cls.objects.get(order_id=order_id)
        order.status = 2
        order.save()

        return order


# 单件商品订单
class SinglePurchaseOrder(models.Model):
    STATUS_ITEMS = (
        (1, '待发货'),
        (2, '正在出库'),
        (3, '已出库'),
        (4, '派送中'),
        (5, '确认收货'),
        (6, '待评价'),
        (7, '已完成'),
    )

    purchase_id = models.CharField(default=GetId.getOrderId(), max_length=18, verbose_name='单件商品订单号')
    info = JSONField(verbose_name='商品信息')
    status = models.SmallIntegerField(default=1, choices=STATUS_ITEMS, verbose_name='状态')

    create_time = models.DateTimeField(auto_now_add=True, editable=False, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, editable=False, verbose_name='修改时间')

    commodity = models.ForeignKey(Commodity, on_delete=models.DO_NOTHING, verbose_name='商品')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name='订单')

    class Meta:
        verbose_name = verbose_name_plural = '单件商品订单'
        ordering = ('-create_time',)

    def __str__(self):
        return self.purchase_id

    @classmethod
    def save_data(cls, order_data):
        order_id = GetId.getOrderId()
        while cls.objects.filter(order_id=order_id):
            order_id = GetId.getOrderId()
        info = order_data['info']
        for item in info:
            print(item)

    @classmethod
    def get_all_single_data(cls, buyer):
        to_be_received_data_list = list()
        completed_data_list = list()
        order_data = Order.get_paid_data(buyer)
        for order in order_data:
            temp_data = cls.objects.get(order=order)
            temp_data = cls.serialize_data(temp_data)
            if temp_data['status'] == 7:
                completed_data_list.append(temp_data)
            else:
                to_be_received_data_list.append(temp_data)

        return to_be_received_data_list, completed_data_list

    @classmethod
    def get_single_data(cls, purchase_id):
        data = cls.serialize_data(cls.objects.get(purchase_id=purchase_id))

        return data

    @staticmethod
    def serialize_data(data):
        address = ''.join(eval(data.order.address.region)) + data.order.address.detail

        data_dict = {
            'id': data.id,
            'purchase_id': data.purchase_id,
            'status': data.status,
            'info': data.info,
            'price': data.info['price'],
            'address': {
                'id': data.order.address.id,
                'name': data.order.address.name,
                'address': address,
                'phone': data.order.address.phone
            },
            'create_time': data.create_time,
            'update_time': data.update_time,
            'is_single': True
        }

        return data_dict


# 买家评论已收货订单的商品
class CommodityComment(models.Model):
    STATUS_ITEMS = (
        (1, '正常'),
        (0, '删除'),
    )

    content = models.TextField(verbose_name='评论内容')
    commodity_star = models.SmallIntegerField(verbose_name='商品质量')
    shop_star = models.SmallIntegerField(verbose_name='商家服务')
    logistics_star = models.SmallIntegerField(verbose_name='物流服务')
    label = ListTextField(base_field=models.CharField(max_length=50))
    status = models.SmallIntegerField(choices=STATUS_ITEMS, verbose_name='状态')

    create_time = models.DateTimeField(auto_now_add=True, editable=False, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, editable=False, verbose_name='修改时间')

    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE, verbose_name='买家')
    single_purchase_order = models.ForeignKey(SinglePurchaseOrder, on_delete=models.DO_NOTHING, verbose_name='单件商品订单')

    class Meta:
        verbose_name = verbose_name_plural = '评论'

    def __str__(self):
        return self.content


# 二级评论
class SecondComment(models.Model):
    STATUS_ITEMS = (
        (1, '正常'),
        (0, '删除'),
    )

    content = models.TextField(verbose_name='评论内容')
    status = models.SmallIntegerField(choices=STATUS_ITEMS, verbose_name='状态')

    create_time = models.DateTimeField(auto_now_add=True, editable=False, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, editable=False, verbose_name='修改时间')

    parent = models.ForeignKey(CommodityComment, on_delete=models.CASCADE, verbose_name='父级评论')

    class Meta:
        verbose_name = verbose_name_plural = '二级评论'

    def __str__(self):
        return self.content


# 评论点赞
class CommentPaise(models.Model):
    status = models.BooleanField(verbose_name='状态')

    create_time = models.DateTimeField(auto_now_add=True, editable=False, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, editable=False, verbose_name='修改时间')

    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE, verbose_name='买家')
    first_comment = models.ForeignKey(CommodityComment, on_delete=models.CASCADE, null=True, verbose_name='一级评论')
    second_comment = models.ForeignKey(SecondComment, on_delete=models.CASCADE, null=True, verbose_name='二级评论')

    class Meta:
        verbose_name = verbose_name_plural = '评论点赞'


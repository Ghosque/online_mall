import json

from django.db import models
from django.contrib.auth.models import User
from django.utils.html import format_html


# 买家
class Buyer(models.Model):
    GENDER_ITEM = (
        (0, '未知'),
        (1, '男'),
        (2, '女')
    )

    open_id = models.CharField(max_length=500, verbose_name='应用ID')
    username = models.CharField(max_length=500, verbose_name='昵称')
    gender = models.IntegerField(choices=GENDER_ITEM, verbose_name='性别')
    avatar = models.CharField(max_length=500, verbose_name='头像')
    language = models.CharField(max_length=100, verbose_name='语言')
    area = models.CharField(max_length=100, verbose_name='地区')
    reward_points = models.IntegerField(default=0, verbose_name='积分')

    create_time = models.DateTimeField(auto_now_add=True, editable=False, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, editable=False, verbose_name='修改时间')

    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='User', related_name='buyer')

    def avatar_data(self):
        return format_html(
            '<img src="{}" style="width:40px;height:40px;" />'.format(self.avatar)
        )
    avatar_data.short_description = '头像'

    class Meta:
        verbose_name = verbose_name_plural = '买家'

    def __str__(self):
        return self.username

    @classmethod
    def create_or_update_user(cls, user_data):
        try:
            user, created_1 = User.objects.update_or_create(password='youhavenopassword', username=user_data['open_id'],
                                                            is_superuser=0, is_staff=1)
            buyer, created_2 = cls.objects.update_or_create(open_id=user_data['open_id'], username=user_data['username'],
                                                            gender=user_data['gender'], avatar=user_data['avatar'],
                                                            language=user_data['language'], area=user_data['area'],
                                                            user=user, defaults={'open_id': user_data['open_id']})
        except Exception as e:
            return None
        else:
            return user, buyer


# 地址
class Address(models.Model):
    name = models.CharField(max_length=15, verbose_name='收件人')
    phone = models.CharField(max_length=15, verbose_name='联系方式')
    region = models.CharField(max_length=300, verbose_name='地区')
    detail = models.CharField(max_length=300, verbose_name='详细地址')

    create_time = models.DateTimeField(auto_now_add=True, editable=False, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, editable=False, verbose_name='修改时间')

    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE, verbose_name='买家')

    class Meta:
        verbose_name = verbose_name_plural = '地址'

    def __str__(self):
        return  self.detail

    @classmethod
    def save_data(cls, data):
        address = cls.objects.create(name=data['name'], phone=data['phone'], region=data['region'],
                                     detail=data['detail'], buyer=data['buyer'])

        return address.id

    @classmethod
    def get_data(cls, buyer):
        addresses = cls.objects.filter(buyer=buyer)
        address_list = list()

        for item in addresses:
            region = eval(item.region)
            phone = item.phone[:3] + '*' * 4 + item.phone[-4:]
            address_list.append({
                'id': item.id,
                'name': item.name,
                'phone': phone,
                'address': ''.join(region)+item.detail,
            })

        return address_list

    @classmethod
    def get_single_data(cls, id):
        address = cls.objects.get(id=id)
        data = {
            'name': address.name,
            'phone': address.phone,
            'region': eval(address.region),
            'detail': address.detail,
        }

        return data

    @classmethod
    def update_data(cls, data_dict):
        try:
            address = cls.objects.get(pk=data_dict['id'])
            address.name = data_dict['name']
            address.phone = data_dict['phone']
            address.region = data_dict['region']
            address.detail = data_dict['detail']
            address.save()
        except:
            return 0
        else:
            return 1

    @classmethod
    def delete_data(cls, id):
        address = cls.objects.get(id=id)
        address.delete()

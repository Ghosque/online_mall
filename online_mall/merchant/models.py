import os
import oss2
import base64
import random
import string
import logging

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django_mysql.models import ListTextField

from common.models import MallUser
from common_function.get_id import GetId

logger = logging.getLogger('scripts')


# 第一类别
class FirstCategory(models.Model):
    STATUS_ITEMS = (
        (settings.CATEGORY_DELETE_STATUS, '删除'),
        (settings.CATEGORY_NORMAL_STATUS, '正常'),
    )

    name = models.CharField(max_length=20, verbose_name='类别名')
    status = models.SmallIntegerField(default=settings.CATEGORY_NORMAL_STATUS, choices=STATUS_ITEMS, verbose_name='状态')

    create_time = models.DateTimeField(auto_now_add=True, editable=False, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, editable=False, verbose_name='修改时间')

    class Meta:
        verbose_name = verbose_name_plural = '第一类别'

    def __str__(self):
        return self.name

    @classmethod
    def get_point_category(cls, pk):
        category_obj = cls.objects.get(pk=pk)

        return category_obj.name


# 第二类别
class SecondCategory(models.Model):
    STATUS_ITEMS = (
        (settings.CATEGORY_DELETE_STATUS, '删除'),
        (settings.CATEGORY_NORMAL_STATUS, '正常'),
    )

    name = models.CharField(max_length=20, verbose_name='类别名')
    status = models.SmallIntegerField(default=settings.CATEGORY_NORMAL_STATUS, choices=STATUS_ITEMS, verbose_name='状态')

    create_time = models.DateTimeField(auto_now_add=True, editable=False, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, editable=False, verbose_name='修改时间')

    first_category = models.ForeignKey(FirstCategory, on_delete=models.CASCADE, verbose_name='第一类别')

    class Meta:
        verbose_name = verbose_name_plural = '第二类别'

    def __str__(self):
        return self.name

    @classmethod
    def get_point_category(cls, pk):
        category_obj = cls.objects.get(pk=pk)

        return category_obj.name


# 第三类别
class ThirdCategory(models.Model):
    STATUS_ITEMS = (
        (settings.CATEGORY_DELETE_STATUS, '删除'),
        (settings.CATEGORY_NORMAL_STATUS, '正常'),
    )

    name = models.CharField(max_length=20, verbose_name='类别名')
    status = models.SmallIntegerField(default=settings.CATEGORY_NORMAL_STATUS, choices=STATUS_ITEMS, verbose_name='状态')

    create_time = models.DateTimeField(auto_now_add=True, editable=False, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, editable=False, verbose_name='修改时间')

    second_category = models.ForeignKey(SecondCategory, on_delete=models.CASCADE, verbose_name='第二类别')

    class Meta:
        verbose_name = verbose_name_plural = '第三类别'

    def __str__(self):
        return self.name

    @classmethod
    def get_category(cls):
        category_list = []

        first_category_list = FirstCategory.objects.filter(status=1)
        for first_category in first_category_list:
            f_name = first_category.name
            f_id = first_category.id
            temp_f_dict = {
                'value': f_id,
                'label': f_name,
                'children': []
            }

            second_category_list = SecondCategory.objects.filter(first_category=first_category, status=1)
            for second_category in second_category_list:
                s_name = second_category.name
                s_id = second_category.id
                temp_s_dict = {
                    'value': s_id,
                    'label': s_name,
                    'children': []
                }

                third_category_list = ThirdCategory.objects.filter(second_category=second_category, status=1)
                for third_category in third_category_list:
                    t_name = third_category.name
                    t_id = third_category.id
                    temp_t_dict = {
                        'value': t_id,
                        'label': t_name
                    }

                    temp_s_dict['children'].append(temp_t_dict)

                temp_f_dict['children'].append(temp_s_dict)

            category_list.append(temp_f_dict)

        return category_list

    @classmethod
    def get_point_category(cls, pk):
        category_obj = cls.objects.get(pk=pk)

        return category_obj.name


# 商家
class Merchant(models.Model):
    merchant_id = models.CharField(default=GetId.getId(), max_length=15, verbose_name='商家ID')
    create_time = models.DateTimeField(auto_now_add=True, editable=False, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, editable=False, verbose_name='修改时间')

    mall_user = models.OneToOneField(MallUser, on_delete=models.CASCADE, verbose_name='mall_user', related_name='merchant')

    class Meta:
        verbose_name = verbose_name_plural = '商家'

    def __str__(self):
        return self.mall_user


# 商家上传图片
class MerchantImage(models.Model):
    TYPE_ITEM = (
        (settings.COVER_IMAGE, '封面'),
        (settings.DISPLAY_IMAGE, '照片墙'),
        (settings.COLOR_IMAGE, '颜色分类'),
    )

    name = models.CharField(max_length=500, verbose_name='文件名')
    oss_object = models.CharField(max_length=500, verbose_name='oss对象')
    img = models.CharField(max_length=500, verbose_name='图片链接')
    img_type = models.SmallIntegerField(choices=TYPE_ITEM, verbose_name='类型')
    status = models.BooleanField(default=True, verbose_name='状态')

    create_time = models.DateTimeField(auto_now_add=True, editable=False, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, editable=False, verbose_name='修改时间')

    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE, verbose_name='商家')

    class Meta:
        verbose_name = verbose_name_plural = '商家上传图片'

    def __str__(self):
        return self.img

    @classmethod
    def upload_image(cls, img_key, img_path):
        bucket = settings.OSS_BUCKET
        bucket.put_object_from_file(img_key, img_path)

        image_url = bucket.sign_url('GET', img_key, 5*12*30*24*60*60)

        return image_url

    @classmethod
    def get_point_merchant_images(cls, user_id, img_type):
        merchant = User.objects.get(pk=user_id).mall_user.merchant
        image_list = cls.objects.filter(merchant=merchant, img_type=img_type, status=True)
        img_list = []
        for image in image_list:
            img_list.append(
                {
                    'id': image.id,
                    'img': image.img
                }
            )

        return img_list

    @classmethod
    def get_name(cls, img_name, user_id):
        name = '/'.join([user_id, img_name])
        image_obj = cls.objects.filter(name=name, status=True)
        while len(image_obj) > 0:
            random_str = ''.join(random.sample(string.ascii_letters + string.digits, 6))
            new_img_name = '_'.join([os.path.splitext(img_name)[0], random_str]) + os.path.splitext(img_name)[1]
            name = '/'.join([user_id, new_img_name])
            image_obj = cls.objects.filter(name=name)

        return name

    @classmethod
    def delete_images(cls, delete_list):
        bucket = settings.OSS_BUCKET
        for item in delete_list:
            item_obj = cls.objects.get(id=item)
            bucket.delete_object(item_obj.oss_object)
            item_obj.status = False
            item_obj.save()


# 商店
class Shop(models.Model):
    STATUS_ITEMS = (
        (settings.SHOP_DELETE_STATUS, '删除'),
        (settings.SHOP_NORMAL_STATUS, '正常'),
        (settings.SHOP_IN_REVIEW_STATUS, '审核中'),
    )

    shop_id = models.CharField(default=GetId.getId(), max_length=15, verbose_name='商店ID')
    name = models.CharField(max_length=50, verbose_name='店名')
    star = models.DecimalField(default=4.0, max_digits=2, decimal_places=1, verbose_name='星级')
    status = models.SmallIntegerField(default=settings.SHOP_IN_REVIEW_STATUS, choices=STATUS_ITEMS, verbose_name='状态')

    create_time = models.DateTimeField(auto_now_add=True, editable=False, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, editable=False, verbose_name='修改时间')

    merchant = models.OneToOneField(Merchant, on_delete=models.CASCADE, verbose_name='商家', related_name='shop')

    class Meta:
        verbose_name = verbose_name_plural = '商店'
        unique_together = ('shop_id', 'name',)

    def __str__(self):
        return self.name

    @classmethod
    def get_shop_info(cls, shop_id):
        return cls.objects.get(shop_id=shop_id)


# 商品
class Commodity(models.Model):
    STATUS_ITEMS = (
        (settings.COMMODITY_DELETE_STATUS, '删除'),
        (settings.COMMODITY_NORMAL_STATUS, '正常'),
        (settings.COMMODITY_IN_REVIEW_STATUS, '审核中'),
        (settings.COMMODITY_OFF_SHELF_STATUS, '下架'),
    )

    commodity_id = models.CharField(default=GetId.getId(), max_length=15, verbose_name='商品ID', unique=True)
    name = models.CharField(max_length=50, verbose_name='商品名称')
    title = models.CharField(max_length=500, verbose_name='详情页标题')
    title_desc = models.CharField(max_length=200, verbose_name='预览页标题')
    cover = models.CharField(max_length=300, verbose_name='预览页封面')
    display_images = ListTextField(base_field=models.CharField(max_length=300), size=10, verbose_name='图片展示')
    status = models.SmallIntegerField(default=settings.COMMODITY_IN_REVIEW_STATUS, choices=STATUS_ITEMS, verbose_name='状态')
    inventory = models.IntegerField(verbose_name='库存')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='价格')

    create_time = models.DateTimeField(auto_now_add=True, editable=False, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, editable=False, verbose_name='修改时间')

    category = models.ForeignKey(ThirdCategory, on_delete=models.CASCADE, verbose_name='类别')
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, verbose_name='商店')

    class Meta:
        verbose_name = verbose_name_plural = '商品'

    def __str__(self):
        return self.title

    @classmethod
    def get_commodity(cls, user_id, status):
        return cls.objects.filter(shop=User.objects.get(pk=user_id).mall_user.merchant.shop, status=status)


# 商品颜色（分类）
class CommodityColor(models.Model):
    commodity_class = models.CharField(max_length=5000, verbose_name='分类')

    create_time = models.DateTimeField(auto_now_add=True, editable=False, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, editable=False, verbose_name='修改时间')

    commodity = models.ForeignKey(Commodity, on_delete=models.CASCADE, verbose_name='商品')

    class Meta:
        verbose_name = verbose_name_plural = '商品分类'

    def __str__(self):
        return self.commodity_class

    @classmethod
    def get_appoint_color(cls, commodity_obj):
        return cls.objects.get(commodity=commodity_obj)


# 商品详情（规格）
class Specification(models.Model):
    information = models.CharField(max_length=5000, verbose_name='详情')

    create_time = models.DateTimeField(auto_now_add=True, editable=False, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, editable=False, verbose_name='修改时间')

    commodity = models.ForeignKey(Commodity, on_delete=models.CASCADE, verbose_name='商品')

    class Meta:
        verbose_name = verbose_name_plural = '商品详情'

    def __str__(self):
        return self.information

    @classmethod
    def get_point_spectification(cls, commodity_obj):
        return cls.objects.get(commodity=commodity_obj)


# 后台管理单元大类
class BackStageFirst(models.Model):

    name = models.CharField(max_length=20, verbose_name='单元名称')
    status = models.BooleanField(default=True, verbose_name='状态')

    create_time = models.DateTimeField(auto_now_add=True, editable=False, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, editable=False, verbose_name='修改时间')

    class Meta:
        verbose_name = verbose_name_plural = '后台管理单元（大类）'

    def __str__(self):
        return self.name


# 后台管理单元小类
class BackStageSecond(models.Model):

    name = models.CharField(max_length=20, verbose_name='单元名称')
    status = models.BooleanField(default=True, verbose_name='状态')

    create_time = models.DateTimeField(auto_now_add=True, editable=False, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, editable=False, verbose_name='修改时间')

    first = models.ForeignKey(BackStageFirst, on_delete=models.CASCADE, verbose_name='大类')

    class Meta:
        verbose_name = verbose_name_plural = '后台管理单元（小类）'

    def __str__(self):
        return self.name

    @classmethod
    def get_back_stage_data(cls):
        back_stage_list = []
        first_list = BackStageFirst.objects.filter(status=True)
        for index_1, first_item in enumerate(first_list):
            temp_dict = {'id': str(index_1+1), 'name': first_item.name, 'child': {}}
            second_list = cls.objects.filter(status=True, first=first_item)
            for index_2, second_item in enumerate(second_list):
                temp_dict['child']['child-{}'.format(index_2+1)] = {
                    'id': '{}-{}'.format(index_1+1, index_2+1),
                    'name': second_item.name
                }

            back_stage_list.append(temp_dict)

        back_stage_dict = {'navigation': back_stage_list}

        return back_stage_dict

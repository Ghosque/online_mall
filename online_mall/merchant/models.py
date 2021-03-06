import os
import base64
import random
import string
import logging

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models

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
    image = models.CharField(max_length=500, verbose_name='图片')
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
                    t_image = third_category.image
                    temp_t_dict = {
                        'value': t_id,
                        'label': t_name,
                        'image':t_image
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
    GENDER_ITEMS = (
        (0, '女'),
        (1, '男'),
        (2, '保密')
    )

    merchant_id = models.CharField(default=GetId.getId(), max_length=15, verbose_name='商家ID')
    name = models.CharField(max_length=50, verbose_name='姓名')
    gender = models.SmallIntegerField(choices=GENDER_ITEMS, verbose_name='性别')
    phone = models.CharField(max_length=15, verbose_name='手机号码', unique=True)
    id_card = models.CharField(max_length=18, verbose_name='身份证号码', unique=True)

    create_time = models.DateTimeField(auto_now_add=True, editable=False, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, editable=False, verbose_name='修改时间')

    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='User', related_name='merchant')

    class Meta:
        verbose_name = verbose_name_plural = '商家'

    def __str__(self):
        return self.name


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
        merchant = User.objects.get(pk=user_id).merchant
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

    @classmethod
    def get_image_base64_data(cls, image_obj):
        image = settings.OSS_BUCKET.get_object(image_obj)
        base64_data = base64.b64encode(image.read())
        image_data = 'data:image/png;base64,' + base64_data.decode('utf-8')

        return image_data

    @classmethod
    def get_image_oss_object(cls, image):
        return cls.objects.get(img=image).oss_object

    @classmethod
    def get_image_img(cls, id):
        return cls.objects.get(id=id).img


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

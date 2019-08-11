import hashlib
import logging
from django.db import models
from django_mysql.models import JSONField, ListTextField
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError
from django.conf import settings

from common import GetId

logger = logging.getLogger('scripts')


# 第一类别
class FirstCategory(models.Model):
    STATUS_ITEMS = (
        (1, '正常'),
        (0, '删除'),
    )

    name = models.CharField(max_length=20, verbose_name='类别名')
    status = models.SmallIntegerField(default=1, choices=STATUS_ITEMS, verbose_name='状态')

    create_time = models.DateTimeField(auto_now_add=True, editable=False, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, editable=False, verbose_name='修改时间')

    class Meta:
        verbose_name = verbose_name_plural = '第一类别'

    def __str__(self):
        return self.name

    @classmethod
    def get_all_data(cls):
        pass


# 第二类别
class SecondCategory(models.Model):
    STATUS_ITEMS = (
        (1, '正常'),
        (0, '删除'),
    )

    name = models.CharField(max_length=20, verbose_name='类别名')
    status = models.SmallIntegerField(default=1, choices=STATUS_ITEMS, verbose_name='状态')

    create_time = models.DateTimeField(auto_now_add=True, editable=False, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, editable=False, verbose_name='修改时间')

    first_category = models.ForeignKey(FirstCategory, on_delete=models.CASCADE, verbose_name='父类别')

    class Meta:
        verbose_name = verbose_name_plural = '第二类别'

    def __str__(self):
        return self.name


# 商家
class Merchant(models.Model):
    GENDER_ITEMS = (
        (1, '男'),
        (0, '女'),
        (2, '保密')
    )

    merchant_id = models.CharField(default=GetId.getId(), max_length=15, verbose_name='商家ID')
    password = models.CharField(max_length=50, verbose_name='密码')
    name = models.CharField(max_length=20, verbose_name='姓名')
    gender = models.SmallIntegerField(choices=GENDER_ITEMS, verbose_name='性别')
    age = models.IntegerField(verbose_name='年龄')
    phone = models.CharField(max_length=15, verbose_name='手机号码', unique=True)
    id_card = models.CharField(max_length=20, verbose_name='身份证号码', unique=True)

    create_time = models.DateTimeField(auto_now_add=True, editable=False, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, editable=False, verbose_name='修改时间')

    class Meta:
        verbose_name = verbose_name_plural = '商家'

    def __str__(self):
        return self.name

    @staticmethod
    def password_md5(password):
        m = hashlib.md5()
        b = password.encode(encoding='utf-8')
        m.update(b)
        password_md5 = m.hexdigest()

        return password_md5

    @classmethod
    def check_password(cls, phone, password):
        password_md5 = cls.password_md5(password)
        try:
            merchant = cls.objects.get(phone=phone, password=password_md5)
        except ObjectDoesNotExist:
            logger.info('手机：{}，密码：{}，md5加密：{} 尝试登录失败'.format(phone, password, password_md5))
            return 0
        else:
            return merchant

    @classmethod
    def check_data(cls, id_card, phone):
        # 1、身份证前17位分别与 settings.COEFFICIENT_LIST 对应相乘再相加，结果对 11 求余，根据 settings.REMAINDER_DICT 得到余数对应的字符，即为身份证最后一位的字符
        # 2、先后判断手机号与身份证号是否已被注册
        top_17_list = [int(i) for i in id_card[:-1]]
        remainder = sum([i * j for i, j in zip(top_17_list, settings.COEFFICIENT_LIST)]) % 11
        if settings.REMAINDER_DICT.get(remainder) == id_card[-1]:
            if cls.objects.filter(phone=phone):
                result = {'code': 0, 'content': '该手机已被注册'}
            elif cls.objects.filter(id_card=id_card):
                result = {'code': 0, 'content': '该身份证已被注册'}
            else:
                result = {'code': 1}
        else:
            result = {'code': 0, 'content': '非法身份证'}

        return result

    @classmethod
    def insert_data(cls, data_dict):
        id_card = data_dict.get('id_card')
        phone = data_dict.get('phone')
        check_result = cls.check_data(id_card, phone)
        if check_result.get('code'):
            password_md5 = cls.password_md5(data_dict.get('password'))
            data_dict['password'] = password_md5

            cls.objects.create(**data_dict)

        return check_result


# 商店
class Shop(models.Model):
    STATUS_ITEMS = (
        (1, '正常'),
        (0, '删除'),
        (2, '审核中'),
    )

    shop_id = models.CharField(default=GetId.getId(), max_length=15, verbose_name='商店ID')
    name = models.CharField(max_length=50, verbose_name='店名')
    star = models.SmallIntegerField(default=4, verbose_name='星级')
    status = models.SmallIntegerField(choices=STATUS_ITEMS, verbose_name='状态')

    create_time = models.DateTimeField(auto_now_add=True, editable=False, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, editable=False, verbose_name='修改时间')

    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE, verbose_name='商家')

    class Meta:
        verbose_name = verbose_name_plural = '商店'
        unique_together = ('shop_id', 'name',)

    def __str__(self):
        return self.name


# 商品
class Commodity(models.Model):
    STATUS_ITEMS = (
        (1, '正常'),
        (0, '删除'),
        (2, '审核中'),
    )

    commodity_id = models.CharField(default=GetId.getId(), max_length=15, verbose_name='商品ID')
    title = models.CharField(max_length=500, verbose_name='详情页标题')
    title_desc = models.CharField(max_length=200, verbose_name='预览页标题')
    url = models.URLField(verbose_name='商品url')
    cover = models.ImageField(verbose_name='预览页封面', upload_to='commodity/cover/')
    status = models.SmallIntegerField(choices=STATUS_ITEMS, verbose_name='状态')
    inventory = models.IntegerField(verbose_name='库存')

    create_time = models.DateTimeField(auto_now_add=True, editable=False, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, editable=False, verbose_name='修改时间')

    category = models.ForeignKey(SecondCategory, on_delete=models.CASCADE, verbose_name='类别')
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, verbose_name='商店')

    class Meta:
        verbose_name = verbose_name_plural = '商品'
        unique_together = ('commodity_id', 'url',)

    def __str__(self):
        return self.title


# 商品颜色（分类）
class CommodityColor(models.Model):
    commodity_class = JSONField(verbose_name='分类')
    size = ListTextField(base_field=models.CharField(max_length=20), size=50, verbose_name='尺寸')

    create_time = models.DateTimeField(auto_now_add=True, editable=False, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, editable=False, verbose_name='修改时间')

    commodity = models.ForeignKey(Commodity, on_delete=models.CASCADE, verbose_name='商品')

    class Meta:
        verbose_name = verbose_name_plural = '商品分类'

    def __str__(self):
        return self.commodity_class


# 商品详情（规格）
class Specification(models.Model):
    infomation = JSONField(verbose_name='详情')

    create_time = models.DateTimeField(auto_now_add=True, editable=False, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, editable=False, verbose_name='修改时间')

    commodity = models.ForeignKey(Commodity, on_delete=models.CASCADE, verbose_name='商品')

    class Meta:
        verbose_name = verbose_name_plural = '商品详情'

    def __str__(self):
        return self.infomation


# 后台管理单元
class BackStage(models.Model):

    name = models.CharField(max_length=20, verbose_name='单元名称')
    status = models.BooleanField(default=True, verbose_name='状态')

    create_time = models.DateTimeField(auto_now_add=True, editable=False, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, editable=False, verbose_name='修改时间')

    class Meta:
        verbose_name = verbose_name_plural = '后台管理单元'

    def __str__(self):
        return self.name

    @classmethod
    def get_back_stage_data(cls):
        return cls.objects.filter(status=True)

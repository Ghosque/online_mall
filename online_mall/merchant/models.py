from django.db import models
from django_mysql.models import JSONField, ListTextField

from common import GetId


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

    name = models.CharField(max_length=20, verbose_name='姓名')
    gender = models.SmallIntegerField(choices=GENDER_ITEMS, verbose_name='性别')
    age = models.IntegerField(verbose_name='年龄')
    phone = models.CharField(max_length=15, verbose_name='手机号码')
    id_card = models.CharField(max_length=20, verbose_name='身份证号码')

    create_time = models.DateTimeField(auto_now_add=True, editable=False, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, editable=False, verbose_name='修改时间')

    class Meta:
        verbose_name = verbose_name_plural = '商家'
        unique_together = ('phone', 'id_card',)

    def __str__(self):
        return self.name


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


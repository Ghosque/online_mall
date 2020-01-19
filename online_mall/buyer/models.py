from django.db import models
from django.conf import settings
import datetime

from merchant.models import Commodity


# 买家
class Buyer(models.Model):
    GENDER_ITEM = (
        (0, '未知'),
        (1, '男'),
        (2, '女')
    )

    open_id = models.CharField(max_length=500, verbose_name='应用ID')
    nickname = models.CharField(max_length=500, verbose_name='昵称')
    gender = models.IntegerField(choices=GENDER_ITEM, verbose_name='性别')
    avatar = models.CharField(max_length=500, verbose_name='头像')
    language = models.CharField(max_length=100, verbose_name='语言')
    area = models.CharField(max_length=100, verbose_name='地区')
    reward_points = models.IntegerField(default=0, verbose_name='积分')

    create_time = models.DateTimeField(auto_now_add=True, editable=False, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, editable=False, verbose_name='修改时间')

    class Meta:
        verbose_name = verbose_name_plural = '买家'

    def __str__(self):
        return self.nickname

    @classmethod
    def create_or_update_user(cls, user_data):
        print(user_data)
        defaults = {'open_id': user_data['open_id']}
        try:
            obj, created = cls.objects.update_or_create(open_id=user_data['open_id'], nickname=user_data['nickname'],
                                                        gender=user_data['gender'], avatar=user_data['avatar'],
                                                        language=user_data['language'], area=user_data['area'],
                                                        defaults={'open_id': user_data['open_id']},)

        except Exception as e:
            print(e)
            return 0
        else:
            return 1


# 买家关注商品
class FollowCommodity(models.Model):
    STATUS_ITEMS = (
        (1, '正常'),
        (0, '删除'),
    )

    status = models.SmallIntegerField(choices=STATUS_ITEMS, verbose_name='状态')

    create_time = models.DateTimeField(auto_now_add=True, editable=False, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, editable=False, verbose_name='修改时间')

    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE, verbose_name='买家')
    commodity = models.ForeignKey(Commodity, on_delete=models.DO_NOTHING, verbose_name='商品')

    class Meta:
        verbose_name = verbose_name_plural = '商品关注'

    @classmethod
    def get_follow_num(cls, buyer):
        follow_list = cls.objects.filter(buyer=buyer)
        return len(follow_list)


# 商品浏览
class CommodityView(models.Model):
    create_time = models.DateTimeField(auto_now_add=True, editable=False, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, editable=False, verbose_name='修改时间')

    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE, verbose_name='买家')
    commodity = models.ForeignKey(Commodity, on_delete=models.DO_NOTHING, verbose_name='商品')

    class Meta:
        verbose_name = verbose_name_plural = '商品浏览'

    @classmethod
    def get_user_view(cls, buyer):
        date_limit_days_ago = datetime.timedelta(days=-settings.TRACE_LIMIT_DAY)
        view_list = cls.objects.filter(buyer=buyer, update_time__gte=date_limit_days_ago)

        return view_list


# 省
class Province(models.Model):
    province_id = models.CharField(max_length=10, verbose_name='省份编码')
    province = models.CharField(max_length=20, verbose_name='省份名')

    create_time = models.DateTimeField(auto_now_add=True, editable=False, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, editable=False, verbose_name='修改时间')

    class Meta:
        verbose_name = verbose_name_plural = '省份'

    def __str__(self):
        return self.province


# 市
class City(models.Model):
    city_id = models.CharField(max_length=10, verbose_name='城市编码')
    city = models.CharField(max_length=20, verbose_name='城市名')

    province = models.ForeignKey(Province, on_delete=models.CASCADE, verbose_name='省份')

    create_time = models.DateTimeField(auto_now_add=True, editable=False, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, editable=False, verbose_name='修改时间')

    class Meta:
        verbose_name = verbose_name_plural = '城市'

    def __str__(self):
        return self.city


# 区/县
class Area(models.Model):
    area_id = models.CharField(max_length=10, verbose_name='区县编码')
    area = models.CharField(max_length=20, verbose_name='区县名')

    city = models.ForeignKey(City, on_delete=models.CASCADE, verbose_name='城市')

    create_time = models.DateTimeField(auto_now_add=True, editable=False, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, editable=False, verbose_name='修改时间')

    class Meta:
        verbose_name = verbose_name_plural = '区/县'

    def __str__(self):
        return self.area


# 地址
class Address(models.Model):
    detail_address = models.CharField(max_length=300, verbose_name='详细地址')
    contact = models.CharField(max_length=15, verbose_name='联系方式')
    addressee = models.CharField(max_length=15, verbose_name='收件人')
    is_default = models.BooleanField(verbose_name='是否为默认地址')

    create_time = models.DateTimeField(auto_now_add=True, editable=False, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, editable=False, verbose_name='修改时间')

    province = models.ForeignKey(Province, on_delete=models.CASCADE, verbose_name='省份')
    city = models.ForeignKey(City, on_delete=models.CASCADE, verbose_name='城市')
    area = models.ForeignKey(Area, on_delete=models.CASCADE, verbose_name='区县')

    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE, verbose_name='买家')

    class Meta:
        verbose_name = verbose_name_plural = '地址'

    def __str__(self):
        return '{}-{}-{}-{}'.format(self.province, self.city, self.area, self.detail_address)

from django.db import models
from django.contrib.auth.models import User


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

    class Meta:
        verbose_name = verbose_name_plural = '买家'

    def __str__(self):
        return self.username

    @classmethod
    def create_or_update_user(cls, user_data):
        try:
            user, created_1 = User.objects.update_or_create(password='nothing', username=user_data['open_id'],
                                                            is_superuser=0, is_staff=1)
            buyer, created_2 = cls.objects.update_or_create(open_id=user_data['open_id'], username=user_data['username'],
                                                            gender=user_data['gender'], avatar=user_data['avatar'],
                                                            language=user_data['language'], area=user_data['area'],
                                                            user=user, defaults={'open_id': user_data['open_id']})
        except Exception as e:
            return None
        else:
            return user, buyer


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

    @classmethod
    def get_all(cls):
        p_objects = cls.objects.all()
        p_dict = dict()
        for item in p_objects:
            p_dict[item.id] = item.province

        return p_dict


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

    @classmethod
    def get_all(cls):
        c_objects = cls.objects.all()
        c_dict = dict()
        for item in c_objects:
            if item.province.id not in c_dict:
                c_dict[item.province.id] = [{item.id: item.city}]
            else:
                c_dict[item.province.id].append({item.id: item.city})

        return c_dict


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

    @classmethod
    def get_all(cls):
        a_objects = cls.objects.all()
        a_dict = dict()
        for item in a_objects:
            if item.city.id not in a_dict:
                a_dict[item.city.id] = [{item.id: item.area}]
            else:
                a_dict[item.city.id].append({item.id: item.area})

        return a_dict


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

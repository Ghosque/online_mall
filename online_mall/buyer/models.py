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


# 地址
class Address(models.Model):
    detail_address = models.CharField(max_length=300, verbose_name='详细地址')
    contact = models.CharField(max_length=15, verbose_name='联系方式')
    addressee = models.CharField(max_length=15, verbose_name='收件人')

    create_time = models.DateTimeField(auto_now_add=True, editable=False, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, editable=False, verbose_name='修改时间')

    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE, verbose_name='买家')

    class Meta:
        verbose_name = verbose_name_plural = '地址'

    def __str__(self):
        return  self.detail_address

    @classmethod
    def save_data(cls, data):
        address = cls.objects.create(detail_address=data['detail_address'], contact=data['contact'],
                                     addressee=data['addressee'], buyer=data['buyer'])

        return address.id

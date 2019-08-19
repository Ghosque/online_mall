from django.db import models
from django.contrib.auth.models import User


class MallUser(models.Model):
    GENDER_ITEMS = (
        (0, '女'),
        (1, '男'),
        (2, '保密')
    )

    name = models.CharField(max_length=50, verbose_name='姓名')
    gender = models.SmallIntegerField(choices=GENDER_ITEMS, verbose_name='性别')
    phone = models.CharField(max_length=15, verbose_name='手机号码', unique=True)
    id_card = models.CharField(max_length=18, verbose_name='身份证号码', unique=True)
    is_merchant = models.BooleanField(verbose_name='是否为商家')

    create_time = models.DateTimeField(auto_now_add=True, editable=False, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, editable=False, verbose_name='修改时间')

    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='User')

    class Meta:
        verbose_name = verbose_name_plural = '用户'

    def __str__(self):
        return self.phone


class VerifyCode(models.Model):
    code = models.CharField(max_length=6, verbose_name='验证码')
    phone = models.CharField(max_length=11, verbose_name='手机号码')

    create_time = models.DateTimeField(auto_now_add=True, editable=False, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, editable=False, verbose_name='修改时间')

    class Meta:
        verbose_name = verbose_name_plural = '验证码'

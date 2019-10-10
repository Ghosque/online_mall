from django.db import models
from django.contrib.auth.models import User


# 商城用户
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

    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='User', related_name='mall_user')

    class Meta:
        verbose_name = verbose_name_plural = '用户'

    def __str__(self):
        return self.phone


# 轮播图
class DisplayImage(models.Model):
    image = models.ImageField(verbose_name='图片', upload_to='display/')
    is_display = models.BooleanField(verbose_name='是否展示')

    create_time = models.DateTimeField(auto_now_add=True, editable=False, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, editable=False, verbose_name='修改时间')

    class Meta:
        verbose_name = verbose_name_plural = '轮播图'

    def __str__(self):
        return self.image

    @classmethod
    def get_display_image(cls):
        return cls.objects.filter(is_display=True)


# 评论标签
class CommentLabel(models.Model):
    label = models.CharField(max_length=50, verbose_name='标签')
    is_delete = models.BooleanField(default=False)

    create_time = models.DateTimeField(auto_now_add=True, editable=False, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, editable=False, verbose_name='修改时间')

    class Meta:
        verbose_name = verbose_name_plural = '评论标签'

    def __str__(self):
        return self.label


# 颜色分类器大类
class FirstColorSelector(models.Model):
    name = models.CharField(max_length=50, verbose_name='名称')
    color_code = models.CharField(max_length=10, verbose_name='颜色代码')
    status = models.BooleanField(default=True, verbose_name='状态')

    create_time = models.DateTimeField(auto_now_add=True, editable=False, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, editable=False, verbose_name='修改时间')

    class Meta:
        verbose_name = verbose_name_plural = '颜色分类器大类'

    def __str__(self):
        return self.name

    @classmethod
    def get_point_color(cls, color_code):
        color_obj = cls.objects.get(color_code=color_code)

        return color_obj.name


# 颜色分类器小类
class SecondColorSelector(models.Model):
    name = models.CharField(max_length=50, verbose_name='名称')
    color_code = models.CharField(max_length=10, verbose_name='颜色代码')
    status = models.BooleanField(default=True, verbose_name='状态')

    create_time = models.DateTimeField(auto_now_add=True, editable=False, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, editable=False, verbose_name='修改时间')

    first = models.ForeignKey(FirstColorSelector, on_delete=models.CASCADE, verbose_name='大类')

    class Meta:
        verbose_name = verbose_name_plural = '颜色分类器小类'

    def __str__(self):
        return self.name

    @classmethod
    def get_color_selector(cls):
        color_selector_list = []

        first_color_selector_list = FirstColorSelector.objects.filter(status=True)
        for first_color_selector in first_color_selector_list:
            f_name = first_color_selector.name
            f_color_code = first_color_selector.color_code
            temp_f_dict = {
                'value': f_color_code,
                'label': f_name,
                'children': []
            }

            second_color_selector_list = SecondColorSelector.objects.filter(first=first_color_selector, status=True)
            for second_color_selector in second_color_selector_list:
                s_name = second_color_selector.name
                s_color_code = second_color_selector.color_code
                temp_s_dict = {
                    'value': s_color_code,
                    'label': s_name,
                }

                temp_f_dict['children'].append(temp_s_dict)

            color_selector_list.append(temp_f_dict)

        return color_selector_list

    @classmethod
    def get_point_color(cls, color_code):
        color_obj = cls.objects.get(color_code=color_code)

        return color_obj.name

    @classmethod
    def get_code_name_dict(cls):
        color_obj_list = cls.objects.filter(status=True)
        code_name_dict = dict()

        for item in color_obj_list:
            code_name_dict[str(item.color_code)] = item.name

        return code_name_dict

import datetime

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django_mysql.models import ListTextField

from common_function.get_id import GetId
from merchant.models import Shop, ThirdCategory
from buyer.models import Buyer


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
    score = models.DecimalField(default=4.0, max_digits=4, decimal_places=2, verbose_name='评分')

    create_time = models.DateTimeField(auto_now_add=True, editable=False, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, editable=False, verbose_name='修改时间')

    category = models.ForeignKey(ThirdCategory, on_delete=models.CASCADE, verbose_name='类别')
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, verbose_name='商店')

    class Meta:
        verbose_name = verbose_name_plural = '商品'

    def __str__(self):
        return self.name

    @classmethod
    def get_commodity(cls, user_id, status):
        commodity_list = cls.objects.filter(shop=User.objects.get(pk=user_id).merchant.shop, status=status)
        data_list = cls.serialize_data(commodity_list)

        return data_list

    @classmethod
    def get_hot_commodity(cls):
        commodity_list = cls.objects.filter(status=1).order_by('-score')[:100]
        data_list = cls.serialize_data(commodity_list)

        return data_list

    @classmethod
    def get_appoint_commodity(cls, id):
        return cls.objects.get(pk=id)

    @classmethod
    def get_appoint_category_commodity(cls, category_id):
        category = ThirdCategory.objects.get(pk=category_id)
        commodity_list = cls.objects.filter(category=category, status=settings.COMMODITY_NORMAL_STATUS).order_by('-score')
        data_list = cls.serialize_data(commodity_list)
        return data_list, category.name

    @classmethod
    def serialize_data(cls, commodity_list):
        data_list = list()
        for item in commodity_list:
            # 获取颜色分类
            color_obj = CommodityColor.get_appoint_color(item)
            # 获取自定义属性
            specification_obj = Specification.get_point_spectification(item)

            single_data = {
                'id': item.id,
                'name': item.name,
                'title': item.title,
                'title_desc': item.title_desc,
                'cover': item.cover,
                'display_images': item.display_images,
                'inventory': item.inventory,
                'price': item.price,
                'category': item.category.id,
                'category_name': item.category.name,
                'color_item': color_obj.commodity_class,
                'attribute_item': specification_obj.information,
                'shop': item.shop.name
            }

            data_list.append(single_data)

        return data_list


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


# 商品评价
class CommodityComment(models.Model):
    content = models.CharField(max_length=1000, verbose_name='内容', null=True, blank=True)
    score = models.IntegerField(verbose_name='评分')

    create_time = models.DateTimeField(auto_now_add=True, editable=False, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, editable=False, verbose_name='修改时间')

    commodity = models.ForeignKey(Commodity, on_delete=models.CASCADE, verbose_name='商品')
    commentator = models.ForeignKey(Buyer, on_delete=models.CASCADE, verbose_name='评论者', related_name='commentator')

    class Meta:
        verbose_name = verbose_name_plural = '商品评论'

    def __str__(self):
        return self.content

    @classmethod
    def get_data(cls, commodity_id):
        commodity = Commodity.objects.get(id=commodity_id)
        all_comments = cls.objects.filter(commodity=commodity)
        all_comments_count = len(all_comments) // 10 * 10
        good_comments = cls.objects.filter(commodity=commodity, score__gte=4)
        if not all_comments:
            good_rate = 0
        else:
            good_rate = format(good_comments/all_comments_count, '.3f')*100

        return all_comments, good_rate


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
            code_name_dict[item.color_code] = item.name

        return code_name_dict


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
    def get_follow(cls, buyer, type=None):
        if type == 'num':
            return cls.objects.filter(buyer=buyer, status=1).count()
        else:
            return cls.objects.filter(buyer=buyer, status=1)

    @classmethod
    def judge_follow(cls, buyer_id, commodity_id):
        if buyer_id == 'null':
            return False
        buyer = Buyer.objects.get(pk=buyer_id)
        commodity = Commodity.objects.get(pk=commodity_id)

        follow_list = cls.objects.filter(buyer=buyer, commodity=commodity, status=1)
        if follow_list:
            return True
        else:
            return False

    @classmethod
    def update_follow(cls, status, buyer_id, commodity_id):
        buyer = Buyer.objects.get(pk=buyer_id)
        commodity = Commodity.objects.get(pk=commodity_id)

        follow_list = cls.objects.filter(buyer=buyer, commodity=commodity)
        if follow_list:
            follow_item = follow_list[0]
            follow_item.status = status
            follow_item.save()
        else:
            cls.objects.create(status=status, buyer=buyer, commodity=commodity)


# 买家关注商家
class FollowShop(models.Model):
    STATUS_ITEMS = (
        (1, '正常'),
        (0, '删除'),
    )

    status = models.SmallIntegerField(choices=STATUS_ITEMS, verbose_name='状态')

    create_time = models.DateTimeField(auto_now_add=True, editable=False, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, editable=False, verbose_name='修改时间')

    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE, verbose_name='买家')
    shop = models.ForeignKey(Shop, on_delete=models.DO_NOTHING, verbose_name='商家')

    class Meta:
        verbose_name = verbose_name_plural = '商家关注'

    @classmethod
    def get_follow(cls, buyer, type):
        if type == 'num':
            return cls.objects.filter(buyer=buyer, status=1).count()
        else:
            return  cls.objects.filter(buyer=buyer, status=1)


# 商品浏览
class CommodityView(models.Model):
    create_time = models.DateTimeField(auto_now_add=True, editable=False, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, editable=False, verbose_name='修改时间')

    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE, verbose_name='买家')
    commodity = models.ForeignKey(Commodity, on_delete=models.DO_NOTHING, verbose_name='商品')

    class Meta:
        verbose_name = verbose_name_plural = '商品浏览'

    @classmethod
    def get_user_view(cls, buyer, type):
        today = datetime.datetime.now()
        offset = datetime.timedelta(days=-settings.TRACE_LIMIT_DAY)
        date_limit_days_ago = (today+offset).strftime('%Y-%m-%d')

        if type == 'num':
            return cls.objects.filter(buyer=buyer, update_time__gte=date_limit_days_ago).count()
        else:
            return cls.objects.filter(buyer=buyer, update_time__gte=date_limit_days_ago)


# 卡券
class CardTicket(models.Model):
    TYPE_ITEM = (
        (0, '满减类'),
        (1, '折扣类')
    )

    type = models.SmallIntegerField(choices=TYPE_ITEM, verbose_name='卡券类型')
    quota = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='额度')
    min_price_limit = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='满减限制')
    deadline = models.DateTimeField(editable=True, verbose_name='截止时间')

    commodity_limit = models.ManyToManyField(Commodity, verbose_name='商品')
    category_limit = models.ManyToManyField(ThirdCategory, verbose_name='种类')

    create_time = models.DateTimeField(auto_now_add=True, editable=False, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, editable=False, verbose_name='修改时间')

    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE, verbose_name='买家')

    class Meta:
        verbose_name = verbose_name_plural = '卡券'

    @classmethod
    def get_card(cls, buyer, type):
        if type == 'num':
            return cls.objects.filter(buyer=buyer).count()
        else:
            return cls.objects.filter(buyer=buyer)
